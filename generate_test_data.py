"""
Generates test_data.jsonl: 100 held-out price-range extraction samples using
templates/phrasings that do NOT appear in generate_dataset.py, to evaluate
generalization of the fine-tuned model(s).

Run: python generate_test_data.py
"""
import json
import random

random.seed(123)

# ---------------------------------------------------------------------------
# Value pools (same pools as training data; wording/templates differ instead)
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
# Templates -- deliberately new phrasing, not present in generate_dataset.py
# ---------------------------------------------------------------------------
RANGE_TEMPLATES = [
    "{product} priced somewhere between {min} and {max}",
    "any {product} ranging {min} to {max}",
    "check {color} {product} costing {min} to {max}",
    "want a {brand} {product}, budget bracket {min}-{max}",
    "{product} valued between {min} and {max}",
    "is there a {product} between {min} and {max}",
    "{product} in {min}-{max} bracket",
    "hunting for {product} priced {min} through {max}",
    "{color} {product} costing anywhere between {min} and {max}",
    "{product} with a price tag of {min} to {max}",
    "{brand} {product} falling between {min} and {max}",
    "{product} between {min} & {max}",
    "need {adjective} {product} ranging from {min} to {max}",
    "{product} priced between roughly {min} and {max}",
    "{product}, {min}-{max} range please",
    "show {product} costing {min} through {max}",
    "{product} valued {min} to {max}",
    "{product} for {min} up to {max}",
    "{brand} {product} between {min} and {max} only",
    "quote me {product} from {min} to {max}",
    "{product} bracketed {min} to {max}",
    "{color} {product} costing from {min} up to {max}",
    "{product} in between {min} and {max} range",
    "{product} priced {min} through to {max}",
    "want {product} costing {min}-{max}",
]

MAX_TEMPLATES = [
    "{product} priced no higher than {max}",
    "keep it under {max} for {product}",
    "{product} capped at {max}",
    "don't want to spend more than {max} on {product}",
    "{color} {product} within {max} budget",
    "{product} for {max} or less",
    "{brand} {product}, ceiling of {max}",
    "{product} shouldn't cost more than {max}",
    "{product} priced under about {max}",
    "give me {product} for max {max}",
    "{product} that's {max} tops",
    "{product} nothing above {max}",
    "{adjective} {product} within {max}",
    "{product} priced sub {max}",
    "{product}, {max} ceiling",
    "affordable {product} within {max} limit",
    "{product} kept below {max}",
    "{product} that stays under {max}",
    "{brand} {product} for no more than {max}",
    "{product} priced {max} max",
    "{product} under a cap of {max}",
    "{color} {product} priced {max} or under",
    "{product} won't go over {max}",
    "{product} in the sub-{max} bracket",
    "{product} for as low as possible, cap {max}",
]

MIN_TEMPLATES = [
    "{product} priced no lower than {min}",
    "{product} starting {min}+",
    "{color} {product} floor of {min}",
    "{product} in the {min} and up bracket",
    "{brand} {product}, {min} minimum",
    "{product} costing {min} or more",
    "{product} north of {min}",
    "{adjective} {product} beyond {min}",
    "{product} priced past {min}",
    "{product} at {min} minimum",
    "{product} floor {min}",
    "{product} starting {min} onward",
    "{brand} {product} costing beyond {min}",
    "{product} that's {min}+",
    "{product} priced {min} upward",
    "{color} {product} costing over {min} at least",
    "{product} not below {min}",
    "{product} in the {min}-plus range",
    "{product} priced from {min} onwards",
    "{product} at minimum {min}",
    "{brand} {product} above the {min} mark",
    "{product} costing north of {min}",
    "{product} higher than {min}",
    "{product} that starts around {min}",
    "{product} priced beyond {min} only",
]

NEITHER_TEMPLATES = [
    "{product} suggestions please",
    "what's a good {product}",
    "{color} {product} options",
    "{brand} {product} specs",
    "{product} comparison",
    "any good {product} out there",
    "{adjective} {product} picks",
    "{product} buying guide",
    "{product} in {color} color",
    "{brand} vs other {product}",
    "{product} for travel",
    "{product} for office use",
    "reliable {product}",
    "{product} unboxing",
    "{product} with fast shipping",
    "{color} {brand} {product} available",
    "{product} in stock",
    "{product} for beginners",
    "portable {product}",
    "{product} deals",
    "{product} discount",
    "waterproof {product}",
    "{product} for outdoors",
    "wireless {product}",
    "{product} with case included",
]

assert len(RANGE_TEMPLATES) == 25
assert len(MAX_TEMPLATES) == 25
assert len(MIN_TEMPLATES) == 25
assert len(NEITHER_TEMPLATES) == 25

CURRENCY_PREFIXES = ["\u20b9{v}", "Rs {v}", "Rs. {v}", "INR {v}"]


def fmt_plain(v):
    return str(v)


def fmt_k(v):
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


FORMAT_NAMES = ["plain", "k", "comma", "currency", "approx"]
FORMAT_WEIGHTS = [0.40, 0.20, 0.15, 0.15, 0.10]


def format_value(v):
    choices = FORMAT_NAMES[:]
    weights = FORMAT_WEIGHTS[:]
    if v < 1000:
        idx = choices.index("k")
        choices.pop(idx)
        weights.pop(idx)

    fmt = random.choices(choices, weights=weights, k=1)[0]
    if fmt == "plain":
        return fmt_plain(v)
    if fmt == "k":
        return fmt_k(v)
    if fmt == "comma":
        return fmt_comma(v)
    if fmt == "currency":
        return fmt_currency(v)
    return fmt_approx(v)


def unique_fill_slots():
    return {
        "product": random.choice(products),
        "color": random.choice(colors),
        "brand": random.choice(brands),
        "adjective": random.choice(adjectives),
    }


# Load training inputs so the test set is guaranteed disjoint from training data
train_inputs = set()
try:
    with open("finetune_data.jsonl", encoding="utf-8") as f:
        for line in f:
            train_inputs.add(json.loads(line)["input"])
except FileNotFoundError:
    pass

used_inputs = set()
samples = []


def build_input(template, slots):
    return f"extract price range: {template.format(**slots)}"


def add_sample(template, slots, min_val, max_val):
    text_input = build_input(template, slots)
    if text_input in used_inputs or text_input in train_inputs:
        return False
    used_inputs.add(text_input)
    output = json.dumps({"min": min_val, "max": max_val})
    samples.append({"input": text_input, "output": output})
    return True


def generate_category(templates, target, kind):
    count = 0
    attempts = 0
    while count < target and attempts < target * 50:
        attempts += 1
        template = templates[count % len(templates)]
        if count % len(templates) == 0 and count > 0:
            random.shuffle(templates)

        slots = unique_fill_slots()
        if kind == "range":
            small, big = sorted(random.sample(price_values, 2))
            reversed_order = random.random() < 0.10
            if reversed_order:
                slots["min"] = format_value(big)
                slots["max"] = format_value(small)
            else:
                slots["min"] = format_value(small)
                slots["max"] = format_value(big)
            ok = add_sample(template, slots, small, big)
        elif kind == "max":
            val = random.choice(price_values)
            slots["max"] = format_value(val)
            ok = add_sample(template, slots, None, val)
        elif kind == "min":
            val = random.choice(price_values)
            slots["min"] = format_value(val)
            ok = add_sample(template, slots, val, None)
        else:
            ok = add_sample(template, slots, None, None)

        if ok:
            count += 1

    assert count == target, f"only generated {count}/{target} for {kind}"


generate_category(RANGE_TEMPLATES, 25, "range")
generate_category(MAX_TEMPLATES, 25, "max")
generate_category(MIN_TEMPLATES, 25, "min")
generate_category(NEITHER_TEMPLATES, 25, "neither")

random.shuffle(samples)

assert len(samples) == 100
assert len(used_inputs) == 100
assert used_inputs.isdisjoint(train_inputs)

with open("test_data.jsonl", "w", encoding="utf-8") as f:
    for s in samples:
        f.write(json.dumps(s, ensure_ascii=False) + "\n")

print("Wrote", len(samples), "samples to test_data.jsonl")
print("Overlap with training inputs:", len(used_inputs & train_inputs))
