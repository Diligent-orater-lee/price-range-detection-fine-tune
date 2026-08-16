"""
Generates finetune_data.jsonl: a price-range extraction fine-tuning dataset
for FLAN-T5-small.

Run: python generate_dataset.py
"""
import json
import random

random.seed(42)

# ---------------------------------------------------------------------------
# Value pools
# ---------------------------------------------------------------------------
products = [
    "shoes", "laptop", "phone", "watch", "bag", "shirt", "camera",
    "headphones", "tablet", "jacket", "sofa", "tv", "monitor",
    "keyboard", "chair", "bicycle", "refrigerator", "microwave",
    "sunglasses", "backpack", "drone", "speaker", "ring", "earbuds",
]

colors = ["red", "blue", "black", "white", "grey", "green", "navy", "brown"]

brands = ["nike", "apple", "samsung", "sony", "dell", "lg", "canon", "bose"]

adjectives = ["cheap", "affordable", "decent", "good", "budget", "premium", "quality"]

price_values = [
    99, 199, 299, 499, 599, 799, 999, 1299, 1499, 1999,
    2499, 2999, 3499, 3999, 4999, 5999, 6999, 7999, 8999, 9999,
    10000, 15000, 20000, 25000, 50000,
]

# ---------------------------------------------------------------------------
# 100 templates: 25 range / 25 max-only / 25 min-only / 25 neither
# ---------------------------------------------------------------------------
RANGE_TEMPLATES = [
    "find {color} {product} between {min} and {max}",
    "show me {product} between {min} and {max}",
    "{product} between {min} and {max}",
    "{product} {min} to {max}",
    "from {min} to {max} for a {product}",
    "looking for a {product} from {min} to {max}",
    "I am looking for products priced between {min} and {max}",
    "I need a {brand} {product} priced between {min} and {max}",
    "{color} {product} priced from {min} to {max}",
    "{product} in the range of {min} to {max}",
    "{product} within {min} and {max}",
    "budget for {product}: {min} to {max}",
    "{brand} {product} costing between {min} and {max}",
    "{adjective} {product} between {min} and {max}",
    "want a {product} somewhere between {min} and {max}",
    "{product} priced anywhere from {min} to {max}",
    "{color} {brand} {product} between {min} and {max}",
    "{product}, budget {min} to {max}",
    "searching {product} between {min} and {max} bucks",
    "{product} that costs between {min} and {max}",
    "need {product} in {min} to {max} range",
    "{product} priced {min}-{max}",
    "{product} somewhere in {min} to {max}",
    "{brand} {product} in {min} to {max} range",
    "{product} between {min} and {max}, {color} preferred",
]

MAX_TEMPLATES = [
    "show me {product} under {max}",
    "{product} under {max}",
    "looking for {product} below {max}",
    "{color} {product} less than {max}",
    "need a {product} no more than {max}",
    "{brand} {product} at most {max}",
    "{product} cheaper than {max}",
    "{product} not exceeding {max}",
    "{product} that won't break the bank over {max}",
    "sumthing under {max} plz",
    "anything {adjective} around {max} ish",
    "{product} roughly around {max}",
    "want {product} for under {max}",
    "{product} priced below {max}",
    "{brand} {product} under {max}",
    "find me {product} within {max}",
    "{product} within a budget of {max}",
    "{product} max {max}",
    "{product}, budget up to {max}",
    "{color} {product} under {max} please",
    "show {product} priced under {max}",
    "need {product}, nothing over {max}",
    "{product} up to {max}",
    "{product} for less than {max}",
    "{adjective} {product} not more than {max}",
]

# templates whose wording already implies approximation
APPROX_WORDED_TEMPLATES = {
    "anything {adjective} around {max} ish",
    "{product} roughly around {max}",
}

MIN_TEMPLATES = [
    "looking for {product} above {min}",
    "{product} above {min}",
    "{brand} {product} over {min}",
    "need {product} more than {min}",
    "{product} at least {min}",
    "{product} starting from {min}",
    "minimum {min} for {product}",
    "{color} {product} over {min}",
    "{product} priced above {min}",
    "want {product} costing more than {min}",
    "{product} with price starting at {min}",
    "{brand} {product} minimum {min}",
    "{product} above {min} only",
    "show me {product} over {min}",
    "{product} that costs more than {min}",
    "{product} not under {min}",
    "high end {product} above {min}",
    "{product} starting {min} and up",
    "{product}, at least {min} range",
    "premium {product} over {min}",
    "need {product} above {min} budget",
    "{product} costing at least {min}",
    "{color} {brand} {product} above {min}",
    "{product} priced from {min} and up",
    "{product} more than {min} preferred",
]

NEITHER_TEMPLATES = [
    "need {adjective} {product}",
    "looking for {color} {product}",
    "show me {brand} {product}",
    "{product} recommendations",
    "best {product} for daily use",
    "{adjective} {color} {product}",
    "{brand} {product} reviews",
    "top rated {product}",
    "{product} with good battery life",
    "stylish {color} {product}",
    "{product} for gifting",
    "durable {product}",
    "{brand} {product} in {color}",
    "affordable {product}",
    "budget {product}",
    "cheap {product}",
    "{product} on sale",
    "trending {product}",
    "{adjective} {brand} {product}",
    "new arrivals {product}",
    "{product} with warranty",
    "comfortable {product}",
    "{color} {product} for men",
    "{product} for women",
    "lightweight {product}",
]

ALL_TEMPLATES = (
    [("range", t) for t in RANGE_TEMPLATES]
    + [("max", t) for t in MAX_TEMPLATES]
    + [("min", t) for t in MIN_TEMPLATES]
    + [("neither", t) for t in NEITHER_TEMPLATES]
)

assert len(RANGE_TEMPLATES) == 25
assert len(MAX_TEMPLATES) == 25
assert len(MIN_TEMPLATES) == 25
assert len(NEITHER_TEMPLATES) == 25

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


# ---- Range samples (250), ~10% (25) with reversed surface order ----------
TARGET_RANGE = 250
REVERSED_TARGET = 25

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

# ---- Max-only samples (250) -----------------------------------------------
TARGET_MAX = 250
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

# ---- Min-only samples (250) -----------------------------------------------
TARGET_MIN = 250
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

# ---- Neither samples (250) -------------------------------------------------
TARGET_NEITHER = 250
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

assert len(samples) == 1000
assert len(used_inputs) == 1000

with open("finetune_data.jsonl", "w", encoding="utf-8") as f:
    for s in samples:
        f.write(json.dumps(s, ensure_ascii=False) + "\n")

print("Wrote", len(samples), "samples to finetune_data.jsonl")
print("Format counts:", format_counts)
