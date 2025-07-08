# === File: trainer.py ===

import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import argparse
from pathlib import Path
import shutil
import json
from trainer_engine import TrainerEngine

def list_cached_models():
    cache_dir = Path(os.getenv("HF_HOME", Path.home() / ".cache" / "huggingface" / "hub"))
    if not cache_dir.exists():
        print("[!] No cached models found.")
        return

    print("\nLocally cached Hugging Face models:")
    for path in cache_dir.glob("models--*"):
        model_name = path.name.replace("models--", "").replace("--", "/")
        print(f" - {model_name}")

def export_to_cache(model_dir, model_name):
    cache_dir = Path.home() / ".cache" / "huggingface" / "custom-models" / model_name
    os.makedirs(cache_dir, exist_ok=True)
    for file in os.listdir(model_dir):
        src = os.path.join(model_dir, file)
        dst = os.path.join(cache_dir, file)
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)
    print(f"\nModel exported to local cache: {cache_dir}")
    print(f"You can now load it using: AutoModel.from_pretrained('{cache_dir}')")

def auto_chunk_size(dataset_path, target_chunks=10, min_size=512):
    with open(dataset_path, "r", encoding="utf-8") as f:
        num_lines = sum(1 for _ in f)
    return max(min_size, num_lines // target_chunks)

def main():
    parser = argparse.ArgumentParser(
        description="Train or resume a language model using chunked datasets and HuggingFace Transformers."
    )

    parser.add_argument(
        "mode", nargs="?", type=str, choices=["new", None],
        help="'new' to start a new training session, omit to resume."
    )
    parser.add_argument("model_name", nargs="?", type=str, help="Base model name (e.g., microsoft/phi-2)")
    parser.add_argument("task_name", nargs="?", type=str, help="Training task name (e.g., product_summary)")
    parser.add_argument("dataset", nargs="?", type=str, help="Dataset filename in ./data/ (e.g., train.jsonl)")

    parser.add_argument("--chunks", type=int, default=1, help="Number of chunks to train this session (default: 1)")
    parser.add_argument("--chunk-size", type=int, help="Samples per chunk. Auto-calculated if omitted.")
    parser.add_argument("--fp16", action="store_true", help="Use mixed-precision (fp16) training")
    parser.add_argument("--max-steps", type=int, help="Max steps per chunk (auto if not set)")
    parser.add_argument("--grad-accum", type=int, help="Gradient accumulation steps (auto if not set)")
    parser.add_argument("--list-models", action="store_true", help="List Hugging Face models cached locally")

    args = parser.parse_args()

    if args.list_models:
        list_cached_models()
        return

    if args.mode == "new":
        if not (args.model_name and args.task_name and args.dataset):
            print("[!] For new mode, please provide model_name, task_name, and dataset.")
            exit()

        dataset_file = (
            args.dataset if args.dataset.endswith(".json") or args.dataset.endswith(".jsonl")
            else args.dataset + ".jsonl"
        )
        dataset_path = os.path.join("data", dataset_file)
        if not os.path.exists(dataset_path):
            print(f"[!] Dataset not found: {dataset_path}")
            exit()

        # Dynamically determine chunk size if not provided
        chunk_size = args.chunk_size or auto_chunk_size(dataset_path)

        # Auto-determined defaults
        config = {
            "chunks": args.chunks,
            "chunk_size": chunk_size,
        }
        if args.fp16:
            config["fp16"] = True
        if args.max_steps:
            config["max_steps"] = args.max_steps
        if args.grad_accum:
            config["grad_accum"] = args.grad_accum

        print("\n[+] Starting new training session...")
        engine = TrainerEngine(
            model_name=args.model_name,
            task_name=args.task_name,
            dataset_name=dataset_file,
            resume=False,
            config=config
        )
    else:
        print("\n[+] Resuming previous training session...")
        config = {}
        if args.chunk_size:
            config["chunk_size"] = args.chunk_size
        if args.chunks:
            config["chunks"] = args.chunks
        if args.fp16:
            config["fp16"] = True
        if args.max_steps:
            config["max_steps"] = args.max_steps
        if args.grad_accum:
            config["grad_accum"] = args.grad_accum

        engine = TrainerEngine(resume=True, config=config)

    engine.train()
    export_to_cache(engine.output_dir, engine.model_name)

    print("\n[✓] Training session complete.")
    print(f"[+] Model path: models/{engine.model_name}/")
    print(f"[+] Task: {engine.task_name}")
    print(f"[+] Dataset: {engine.dataset_name}")

if __name__ == "__main__":
    main()
