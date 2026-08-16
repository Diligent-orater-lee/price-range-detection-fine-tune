"""
Fine-tunes google/flan-t5-small to extract {"min": ..., "max": ...} price
ranges from natural language search queries.

Data: finetune_data.jsonl (lines of {"input": ..., "output": ...})

Usage:
    python finetune.py
    python finetune.py --epochs 5 --batch-size 16 --output-dir ./flan-t5-price-extractor
"""
import argparse

import httpx
import huggingface_hub
import numpy as np
from datasets import load_dataset
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
)

# TEMPORARY: corporate VPN (Cato) injects a self-signed cert into the chain,
# breaking TLS verification on Hub downloads. Remove once the VPN's CA is
# trusted by the system store.
DISABLE_HF_SSL_VERIFY = True
if DISABLE_HF_SSL_VERIFY:
    huggingface_hub.set_client_factory(
        lambda: httpx.Client(verify=False, follow_redirects=True, timeout=None)
    )

MODEL_NAME = "google/flan-t5-small"
DATA_FILE = "finetune_data.jsonl"
MAX_INPUT_LENGTH = 64
MAX_TARGET_LENGTH = 32


def parse_args():
    parser = argparse.ArgumentParser(description="Fine-tune FLAN-T5-small for price range extraction")
    parser.add_argument("--data-file", default=DATA_FILE)
    parser.add_argument("--model-name", default=MODEL_NAME)
    parser.add_argument("--output-dir", default="./flan-t5-price-extractor")
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument("--val-split", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def build_preprocess_fn(tokenizer):
    def preprocess(batch):
        model_inputs = tokenizer(
            batch["input"],
            max_length=MAX_INPUT_LENGTH,
            truncation=True,
        )
        labels = tokenizer(
            text_target=batch["output"],
            max_length=MAX_TARGET_LENGTH,
            truncation=True,
        )
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    return preprocess


def build_compute_metrics(tokenizer):
    def compute_metrics(eval_preds):
        preds, labels = eval_preds
        if isinstance(preds, tuple):
            preds = preds[0]

        preds = np.where(preds != -100, preds, tokenizer.pad_token_id)
        labels = np.where(labels != -100, labels, tokenizer.pad_token_id)

        decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)
        decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)

        exact_matches = sum(
            p.strip() == l.strip() for p, l in zip(decoded_preds, decoded_labels)
        )
        return {"exact_match": exact_matches / len(decoded_labels)}

    return compute_metrics


def main():
    args = parse_args()

    dataset = load_dataset("json", data_files=args.data_file, split="train")
    dataset = dataset.train_test_split(test_size=args.val_split, seed=args.seed)

    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.model_name)

    tokenized = dataset.map(
        build_preprocess_fn(tokenizer),
        batched=True,
        remove_columns=dataset["train"].column_names,
    )

    data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model)

    training_args = Seq2SeqTrainingArguments(
        output_dir=args.output_dir,
        eval_strategy="epoch",
        save_strategy="epoch",
        logging_strategy="steps",
        logging_steps=20,
        learning_rate=args.learning_rate,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        weight_decay=0.01,
        num_train_epochs=args.epochs,
        predict_with_generate=True,
        generation_max_length=MAX_TARGET_LENGTH,
        load_best_model_at_end=True,
        metric_for_best_model="exact_match",
        greater_is_better=True,
        save_total_limit=2,
        report_to="none",
        seed=args.seed,
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized["train"],
        eval_dataset=tokenized["test"],
        processing_class=tokenizer,
        data_collator=data_collator,
        compute_metrics=build_compute_metrics(tokenizer),
    )

    trainer.train()
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)


if __name__ == "__main__":
    main()
