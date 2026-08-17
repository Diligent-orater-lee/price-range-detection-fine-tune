"""
Evaluates every fine-tuned checkpoint under flan-t5-price-extractor/ against
test_data.jsonl and reports accuracy metrics per model.

Run: python evaluate_models.py
"""
import argparse
import json
import re
from pathlib import Path

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

MAX_INPUT_LENGTH = 64
MAX_TARGET_LENGTH = 32

JSON_RE = re.compile(r"\{.*\}")


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate price-range extraction checkpoints")
    parser.add_argument("--test-file", default="test_data.jsonl")
    parser.add_argument(
        "--models-dir",
        default="flan-t5-price-extractor",
        help="Directory containing one or more checkpoint-* subfolders (or a single model dir).",
    )
    parser.add_argument("--batch-size", type=int, default=16)
    return parser.parse_args()


def discover_checkpoints(models_dir):
    root = Path(models_dir)
    checkpoints = sorted(
        (p for p in root.glob("checkpoint-*") if p.is_dir()),
        key=lambda p: int(p.name.split("-")[-1]),
    )
    if checkpoints:
        return checkpoints
    if (root / "config.json").exists():
        return [root]
    raise FileNotFoundError(f"No checkpoints or model found under {models_dir}")


def load_test_data(path):
    samples = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            samples.append((obj["input"], json.loads(obj["output"])))
    return samples


def decode_with_braces(tokenizer, ids):
    """T5's vocab has no `{`/`}` token, so both collapse to <unk> and get
    dropped by skip_special_tokens=True. Decode with specials kept and map
    the leading/trailing <unk> back to the braces the model actually emitted.
    """
    text = tokenizer.decode(ids, skip_special_tokens=False)
    for special in (tokenizer.pad_token, tokenizer.eos_token, tokenizer.bos_token):
        if special:
            text = text.replace(special, "")
    text = text.strip()

    unk = tokenizer.unk_token or "<unk>"
    if text.startswith(unk):
        text = "{" + text[len(unk):]
    if text.endswith(unk):
        text = text[: -len(unk)] + "}"
    return text.strip()


def parse_prediction(text):
    """Best-effort parse of the model's raw generated text into a dict."""
    match = JSON_RE.search(text)
    candidate = match.group(0) if match else text
    try:
        parsed = json.loads(candidate)
        if isinstance(parsed, dict) and "min" in parsed and "max" in parsed:
            return parsed, True
    except (json.JSONDecodeError, ValueError):
        pass
    return {"min": None, "max": None}, False


def evaluate_checkpoint(checkpoint_path, samples, batch_size):
    tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)
    model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint_path)
    model.eval()

    inputs = [s[0] for s in samples]
    expected = [s[1] for s in samples]
    predictions_raw = []

    with torch.no_grad():
        for i in range(0, len(inputs), batch_size):
            batch = inputs[i : i + batch_size]
            enc = tokenizer(
                batch,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=MAX_INPUT_LENGTH,
            )
            out = model.generate(**enc, max_new_tokens=MAX_TARGET_LENGTH, num_beams=1)
            decoded = [decode_with_braces(tokenizer, ids) for ids in out]
            predictions_raw.extend(decoded)

    total = len(samples)
    exact_match = 0
    valid_json = 0
    min_correct = 0
    max_correct = 0
    both_null_correct = 0
    results = []

    for inp, exp, raw in zip(inputs, expected, predictions_raw):
        pred, is_valid = parse_prediction(raw)
        valid_json += int(is_valid)
        min_ok = pred.get("min") == exp["min"]
        max_ok = pred.get("max") == exp["max"]
        min_correct += int(min_ok)
        max_correct += int(max_ok)
        is_exact = min_ok and max_ok
        exact_match += int(is_exact)
        if exp["min"] is None and exp["max"] is None:
            both_null_correct += int(is_exact)
        results.append(
            {"input": inp, "expected": exp, "raw_output": raw, "parsed": pred, "correct": is_exact}
        )

    metrics = {
        "checkpoint": str(checkpoint_path),
        "total": total,
        "exact_match_acc": exact_match / total,
        "valid_json_rate": valid_json / total,
        "min_field_acc": min_correct / total,
        "max_field_acc": max_correct / total,
    }
    return metrics, results


def main():
    args = parse_args()
    samples = load_test_data(args.test_file)
    checkpoints = discover_checkpoints(args.models_dir)

    all_metrics = []
    for ckpt in checkpoints:
        print(f"\n=== Evaluating {ckpt} ===")
        metrics, results = evaluate_checkpoint(ckpt, samples, args.batch_size)
        all_metrics.append(metrics)

        print(f"  Exact match accuracy : {metrics['exact_match_acc']:.2%} ({int(metrics['exact_match_acc'] * metrics['total'])}/{metrics['total']})")
        print(f"  Valid JSON rate      : {metrics['valid_json_rate']:.2%}")
        print(f"  min field accuracy   : {metrics['min_field_acc']:.2%}")
        print(f"  max field accuracy   : {metrics['max_field_acc']:.2%}")

        failures = [r for r in results if not r["correct"]][:5]
        if failures:
            print("  Sample failures:")
            for f in failures:
                print(f"    input   : {f['input']}")
                print(f"    expected: {f['expected']}")
                print(f"    got     : {f['raw_output']!r} -> {f['parsed']}")

        out_path = Path(ckpt).name + "_eval_results.jsonl"
        with open(out_path, "w", encoding="utf-8") as f:
            for r in results:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print("\n=== Summary ===")
    header = f"{'checkpoint':<45}{'exact_match':>13}{'valid_json':>12}{'min_acc':>10}{'max_acc':>10}"
    print(header)
    for m in all_metrics:
        print(
            f"{m['checkpoint']:<45}{m['exact_match_acc']:>13.2%}{m['valid_json_rate']:>12.2%}"
            f"{m['min_field_acc']:>10.2%}{m['max_field_acc']:>10.2%}"
        )


if __name__ == "__main__":
    main()
