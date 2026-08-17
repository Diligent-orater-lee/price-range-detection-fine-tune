"""
Generates finetune_data.jsonl: a price-range extraction fine-tuning dataset
for FLAN-T5-small.

Templates and value pools live in templates.py.

Run: python generate_dataset.py
"""
import json
import random

from templates import (
    APPROX_WORDED_TEMPLATES,
    ADJECTIVES as adjectives,
    BRANDS as brands,
    COLORS as colors,
    MAX_TEMPLATES,
    MIN_TEMPLATES,
    NEITHER_TEMPLATES,
    PRICE_VALUES as price_values,
    PRODUCTS as products,
    RANGE_TEMPLATES,
)

random.seed(42)

# ---------------------------------------------------------------------------
# Number formatting
# ---------------------------------------------------------------------------
CURRENCY_PREFIXES = ["\u20b9{v}", "Rs {v}", "Rs. {v}", "INR {v}"]


def fmt_plain(v):
    return str(v)


def fmt_k(v):
    # e.g. 1299 -> "1.3k", 9999 -> "10k", 15000 -> "15k"
    scaled = round(v / 1000, 1)
    if scaled == int(scaled):
        return f"{int(scaled)}k"
    return f"{scaled}k"


def fmt_comma(v):
    return f"{v:,}"


def fmt_currency(v):
    return random.choice(CURRENCY_PREFIXES).format(v=v)


def fmt_approx(v):
    return random.choice(["around {v}", "roughly {v}"]).format(v=v)


FORMAT_WEIGHTS = {
    "plain": 0.40,
    "k": 0.20,
    "comma": 0.15,
    "currency": 0.15,
    "approx": 0.10,
}
FORMAT_NAMES = list(FORMAT_WEIGHTS.keys())
FORMAT_WEIGHT_VALUES = list(FORMAT_WEIGHTS.values())

format_counts = {k: 0 for k in FORMAT_NAMES}


def format_value(v, allow_approx=True):
    """Pick a display format for value v honoring the target distribution."""
    choices = FORMAT_NAMES[:]
    weights = FORMAT_WEIGHT_VALUES[:]
    if v < 1000:
        # k-suffix doesn't read naturally for sub-1000 values
        idx = choices.index("k")
        choices.pop(idx)
        weights.pop(idx)
    if not allow_approx:
        idx = choices.index("approx")
        choices.pop(idx)
        weights.pop(idx)

    fmt = random.choices(choices, weights=weights, k=1)[0]
    format_counts[fmt] += 1

    if fmt == "plain":
        return fmt_plain(v)
    if fmt == "k":
        return fmt_k(v)
    if fmt == "comma":
        return fmt_comma(v)
    if fmt == "currency":
        return fmt_currency(v)
    return fmt_approx(v)


# ---------------------------------------------------------------------------
# Sample generation
# ---------------------------------------------------------------------------
used_inputs = set()
samples = []


def unique_fill_slots():
    return {
        "product": random.choice(products),
        "color": random.choice(colors),
        "brand": random.choice(brands),
        "adjective": random.choice(adjectives),
    }


def build_input(template, slots):
    text = template.format(**slots)
    return f"extract price range: {text}"


def add_sample(template, slots, min_val, max_val):
    text_input = build_input(template, slots)
    if text_input in used_inputs:
        return False
    used_inputs.add(text_input)
    output = json.dumps({"min": min_val, "max": max_val})
    samples.append({"input": text_input, "output": output})
    return True


# ---- Range samples (1250), ~10% (125) with reversed surface order -------
TARGET_RANGE = 1250
REVERSED_TARGET = 125

range_indices = list(range(TARGET_RANGE))
reversed_indices = set(random.sample(range_indices, REVERSED_TARGET))

count = 0
attempts = 0
while count < TARGET_RANGE and attempts < TARGET_RANGE * 50:
    attempts += 1
    template = RANGE_TEMPLATES[count % len(RANGE_TEMPLATES)]
    # shuffle which template index is picked after each full pass for variety
    if count % len(RANGE_TEMPLATES) == 0 and count > 0:
        random.shuffle(RANGE_TEMPLATES)

    small, big = sorted(random.sample(price_values, 2))
    slots = unique_fill_slots()

    reversed_order = count in reversed_indices
    if reversed_order:
        min_slot_text = format_value(big)
        max_slot_text = format_value(small)
    else:
        min_slot_text = format_value(small)
        max_slot_text = format_value(big)

    slots["min"] = min_slot_text
    slots["max"] = max_slot_text

    if add_sample(template, slots, small, big):
        count += 1

assert count == TARGET_RANGE, f"only generated {count} range samples"

# ---- Max-only samples (1250) -----------------------------------------------
TARGET_MAX = 1250
count = 0
attempts = 0
while count < TARGET_MAX and attempts < TARGET_MAX * 50:
    attempts += 1
    template = MAX_TEMPLATES[count % len(MAX_TEMPLATES)]
    if count % len(MAX_TEMPLATES) == 0 and count > 0:
        random.shuffle(MAX_TEMPLATES)

    val = random.choice(price_values)
    slots = unique_fill_slots()
    allow_approx = template not in APPROX_WORDED_TEMPLATES
    slots["max"] = format_value(val, allow_approx=allow_approx)

    if add_sample(template, slots, None, val):
        count += 1

assert count == TARGET_MAX, f"only generated {count} max-only samples"

# ---- Min-only samples (1250) -----------------------------------------------
TARGET_MIN = 1250
count = 0
attempts = 0
while count < TARGET_MIN and attempts < TARGET_MIN * 50:
    attempts += 1
    template = MIN_TEMPLATES[count % len(MIN_TEMPLATES)]
    if count % len(MIN_TEMPLATES) == 0 and count > 0:
        random.shuffle(MIN_TEMPLATES)

    val = random.choice(price_values)
    slots = unique_fill_slots()
    slots["min"] = format_value(val)

    if add_sample(template, slots, val, None):
        count += 1

assert count == TARGET_MIN, f"only generated {count} min-only samples"

# ---- Neither samples (1250) -------------------------------------------------
TARGET_NEITHER = 1250
count = 0
attempts = 0
while count < TARGET_NEITHER and attempts < TARGET_NEITHER * 200:
    attempts += 1
    template = NEITHER_TEMPLATES[count % len(NEITHER_TEMPLATES)]
    if count % len(NEITHER_TEMPLATES) == 0 and count > 0:
        random.shuffle(NEITHER_TEMPLATES)

    slots = unique_fill_slots()
    if add_sample(template, slots, None, None):
        count += 1

assert count == TARGET_NEITHER, f"only generated {count} neither samples"

# ---------------------------------------------------------------------------
# Shuffle final order and write file
# ---------------------------------------------------------------------------
random.shuffle(samples)

assert len(samples) == 5000
assert len(used_inputs) == 5000

with open("finetune_data.jsonl", "w", encoding="utf-8") as f:
    for s in samples:
        f.write(json.dumps(s, ensure_ascii=False) + "\n")

print("Wrote", len(samples), "samples to finetune_data.jsonl")
print("Format counts:", format_counts)
