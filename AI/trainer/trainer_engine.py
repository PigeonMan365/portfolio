import os
import json
import gc
import math
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    AutoConfig,
    DataCollatorForLanguageModeling
)
from datasets import Dataset

try:
    from bitsandbytes.optim import AdamW8bit
    USE_8BIT = True
except ImportError:
    USE_8BIT = False


class TrainerEngine:
    def __init__(
        self,
        model_name=None,
        task_name=None,
        dataset_name=None,
        resume=False,
        output_name=None,
        config=None,
    ):
        self.resume = resume
        self.base_model_name = model_name
        self.task_name = task_name or "unnamed_task"
        self.dataset_name = dataset_name
        self.output_name = output_name if output_name else "resumed_model"
        self.output_dir = os.path.join("models", self.output_name)
        self.state_file = os.path.join(self.output_dir, "state.json")
        self.model_name = self.output_name
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.config = config or {}

        self.progress_path = os.path.join(self.output_dir, "progress.json")
        self.completed_chunks = set()

        if resume:
            self._load_state()
        else:
            self._prepare_new_session()

        self._load_model_and_tokenizer()
        self._patch_config()
        self._prepare_dataset()

    def _prepare_new_session(self):
        if os.path.exists(self.output_dir):
            print(f"\n[~] Clearing previous model at {self.output_dir}")
            for root, dirs, files in os.walk(self.output_dir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
        os.makedirs(self.output_dir, exist_ok=True)
        self._save_state()

    def _save_state(self):
        state = {
            "base_model_name": self.base_model_name,
            "task_name": self.task_name,
            "dataset_name": self.dataset_name,
            "model_name": self.output_name
        }
        with open(self.state_file, "w") as f:
            json.dump(state, f)

    def _load_state(self):
        if not os.path.exists(self.state_file):
            raise RuntimeError("[!] No previous state found. Cannot resume.")
        with open(self.state_file, "r") as f:
            state = json.load(f)
        self.base_model_name = state["base_model_name"]
        self.task_name = state["task_name"]
        self.dataset_name = state["dataset_name"]
        self.model_name = state["model_name"]
        self.output_dir = os.path.join("models", self.model_name)

        if os.path.exists(self.progress_path):
            with open(self.progress_path) as f:
                self.completed_chunks = set(json.load(f).get("completed_chunks", []))

    def _load_model_and_tokenizer(self):
        print("\n[+] Loading model and tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.base_model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        model_path = self.output_dir if self.resume and os.path.exists(self.output_dir) else self.base_model_name
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16 if self.config.get("fp16", False) else torch.float32,
            low_cpu_mem_usage=True
        )
        self.model.gradient_checkpointing_enable()
        self.model.to(self.device)

    def _patch_config(self):
        config_path = os.path.join(self.output_dir, "config.json")
        if not os.path.exists(config_path):
            AutoConfig.from_pretrained(self.base_model_name).to_json_file(config_path)

        with open(config_path, "r") as f:
            raw = json.load(f)

        if "model_type" not in raw:
            print("[~] Patching config.json with model_type='phi'")
            raw["model_type"] = "phi"
            with open(config_path, "w") as f_out:
                json.dump(raw, f_out, indent=2)

    def _prepare_dataset(self):
        path = os.path.join("data", self.dataset_name)
        with open(path, "r", encoding="utf-8") as f:
            self.offsets = []
            while f.readline():
                self.offsets.append(f.tell())
        self.total_samples = len(self.offsets)
        self.chunk_size = self.config.get("chunk_size", 4000)
        self.num_chunks = math.ceil(self.total_samples / self.chunk_size)
        self.data_file = open(path, "r", encoding="utf-8")

    def _load_chunk(self, idx):
        start = idx * self.chunk_size
        end = min((idx + 1) * self.chunk_size, self.total_samples)
        self.data_file.seek(self.offsets[start])
        samples = [json.loads(self.data_file.readline().strip()) for _ in range(end - start)]
        return Dataset.from_list(samples)

    def _tokenize(self, example):
        tokens = self.tokenizer(
            example["text"],
            padding="max_length",
            truncation=True,
            max_length=self.config.get("max_length", 256),
            return_tensors="pt"
        )
        tokens["labels"] = tokens["input_ids"].clone()
        return {k: v.squeeze(0) for k, v in tokens.items()}

    def train(self):
        max_steps = self.config.get("max_steps", 100)
        grad_accum = self.config.get("grad_accum", 2)
        use_fp16 = self.config.get("fp16", False)
        chunks_to_train = self.config.get("chunks", 1)

        trained = 0
        for idx in range(self.num_chunks):
            if idx in self.completed_chunks:
                continue
            if trained >= chunks_to_train:
                break

            print(f"\n[+] Training chunk {idx + 1}/{self.num_chunks}")
            dataset = self._load_chunk(idx)
            tokenized = dataset.map(self._tokenize, batched=False).remove_columns(["text"])

            targs = TrainingArguments(
                output_dir=self.output_dir,
                overwrite_output_dir=False,
                per_device_train_batch_size=1,
                gradient_accumulation_steps=grad_accum,
                max_steps=max_steps,
                fp16=use_fp16,
                logging_steps=10,
                save_total_limit=1,
                remove_unused_columns=False,
                report_to=[]
            )

            optimizer = (AdamW8bit(self.model.parameters(), lr=5e-5), None) if USE_8BIT else (None, None)

            trainer = Trainer(
                model=self.model,
                args=targs,
                train_dataset=tokenized,
                data_collator=DataCollatorForLanguageModeling(tokenizer=self.tokenizer, mlm=False),
                optimizers=optimizer
            )

            trainer.train()
            self.completed_chunks.add(idx)
            trained += 1

            with open(self.progress_path, "w") as f:
                json.dump({"completed_chunks": sorted(list(self.completed_chunks))}, f)

            del trainer, tokenized, dataset
            torch.cuda.empty_cache()
            gc.collect()

            print(f"[\u2713] Finished chunk {idx + 1}")

        self.model.save_pretrained(self.output_dir)
        self.tokenizer.save_pretrained(self.output_dir)
        print(f"\n[\u2713] Model saved to {self.output_dir}")
