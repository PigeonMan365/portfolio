# AI Trainer

A modular, CLI-based system for training Hugging Face-compatible language models on local ".json" or ".jsonl" datasets.

This framework supports incremental, chunked training, automatic resume, and is designed to run efficiently on low-resource machines such as personal laptops. It is derived from my "url_analist" project after training my first language model.

This project is intended for training models for casual language modeling and next-word prediction tasks.

---

# Features

* Train any Hugging Face-compatible causal language model
* Resume training automatically from the last completed chunk
* Chunked dataset handling to reduce memory usage
* Support for mixed precision (fp16) and 8-bit optimizers (if available)
* Optional Weights & Biases (W&B) integration for experiment tracking
* Local model caching for reuse
* Auto-patches model configs (e.g. for missing "model_type")
* CLI-based, fully scriptable workflow

---

# Project Structure

ai_trainer/
├── data/ # Your datasets (must be JSON/JSONL with a "text" field)
│ └── train.jsonl
├── models/ # Trained models and saved progress
│ └── my_model/
├── trainer.py # CLI interface for training/resuming
├── trainer_engine.py # Core training logic
├── requirements.txt # Python dependencies
├── README.md # This file
└── .gitignore # Prevents data/models from being pushed to GitHub

# Dataset Format

Datasets must be ".json" or ".jsonl" format with a ""text"" field on each line:

{"text": "This is an example training line."}
{"text": "Another example for the model to learn from."}

# Usage

# Start a new training run

python trainer.py new <base_model_name> <new_model_name> <task_name> <dataset>

ex.
python trainer.py new microsoft/phi-2 url_analist url-analysis urls.json

# Resume training

python trainer.py

# List cached Hugging Face models

python trainer.py --list-models

# After training, models are saved under:

models/<model_name>/

# They are also exported to the local Hugging Face cache for easy reuse:

~/.cache/huggingface/custom-models/<model_name>


# Example usage in Python:

from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained("~/.cache/huggingface/custom-models/my_model_name")
