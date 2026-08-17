"""
Template and value-pool definitions for the price-range extraction dataset.

Exposes, after combining short fragment-based templates with hand-written
long/descriptive ones:
    RANGE_TEMPLATES   -- 250 templates containing {min} and {max}
    MAX_TEMPLATES     -- 250 templates containing {max} only
    MIN_TEMPLATES     -- 250 templates containing {min} only
    NEITHER_TEMPLATES -- 250 templates with no price placeholders
(1000 templates total)

Also exposes the value pools used to fill them in:
    PRODUCTS, COLORS, BRANDS, ADJECTIVES, PRICE_VALUES

Templates whose wording already implies approximation (and would read
oddly with an "around"/"roughly" number format layered on top) are listed
in APPROX_WORDED_TEMPLATES.
"""

# ---------------------------------------------------------------------------
# Value pools
# ---------------------------------------------------------------------------
PRODUCTS = [
    "shoes", "laptop", "phone", "watch", "bag", "shirt", "camera",
    "headphones", "tablet", "jacket", "sofa", "tv", "monitor",
    "keyboard", "chair", "bicycle", "refrigerator", "microwave",
    "sunglasses", "backpack", "drone", "speaker", "ring", "earbuds",
    "smartwatch", "printer", "router", "vacuum cleaner", "air conditioner",
    "washing machine", "blender", "iron", "table fan", "trimmer",
    "power bank", "charger", "mouse", "webcam", "projector", "treadmill",
]

COLORS = [
    "red", "blue", "black", "white", "grey", "green", "navy", "brown",
    "yellow", "purple", "pink", "beige", "maroon", "teal",
]

BRANDS = [
    "nike", "apple", "samsung", "sony", "dell", "lg", "canon", "bose",
    "xiaomi", "oneplus", "asus", "hp", "puma", "adidas", "jbl", "whirlpool",
]

ADJECTIVES = [
    "cheap", "affordable", "decent", "good", "budget", "premium", "quality",
    "sturdy", "stylish", "reliable", "elegant", "compact", "value-for-money",
]

PRICE_VALUES = [
    99, 149, 199, 299, 349, 449, 499, 599, 649, 799, 849, 999,
    1099, 1299, 1499, 1999, 2199, 2499, 2999, 3499, 3999, 4999,
    5999, 6999, 7999, 8999, 9999,
    10000, 15000, 20000, 25000, 50000,
]

# ---------------------------------------------------------------------------
# Fragment banks used to build the fragment-combination templates
# ---------------------------------------------------------------------------
_LEADINS = [
    "{product}",
    "{color} {product}",
    "{brand} {product}",
    "{adjective} {product}",
    "show me {product}",
    "show me {color} {product}",
    "looking for {product}",
    "looking for a {product}",
    "looking for a {brand} {product}",
    "find {color} {product}",
    "find me a {product}",
    "need a {product}",
    "need a {brand} {product}",
    "want a {product}",
    "want {adjective} {product}",
    "searching for {product}",
    "searching {product}",
    "hunting for {product}",
    "can you find {product}",
    "do you have {product}",
    "is there a {product}",
    "please show {product}",
    "quote me {product}",
    "check {color} {product}",
    "any {product}",
]

_RANGE_PHRASES = [
    "between {min} and {max}",
    "from {min} to {max}",
    "{min} to {max}",
    "priced from {min} to {max}",
    "priced between {min} and {max}",
    "costing between {min} and {max}",
    "in the range of {min} to {max}",
    "somewhere between {min} and {max}",
    "anywhere from {min} to {max}",
    "in the {min}-{max} bracket",
]

_MAX_PHRASES = [
    "under {max}",
    "below {max}",
    "less than {max}",
    "no more than {max}",
    "at most {max}",
    "cheaper than {max}",
    "not exceeding {max}",
    "capped at {max}",
    "priced under {max}",
    "up to {max}",
]

_MIN_PHRASES = [
    "above {min}",
    "over {min}",
    "more than {min}",
    "at least {min}",
    "starting from {min}",
    "minimum {min}",
    "north of {min}",
    "not below {min}",
    "beyond {min}",
    "priced past {min}",
]

_NEITHER_CORE = [
    "{adjective} {product}",
    "{color} {product}",
    "{brand} {product}",
    "{product} recommendations",
    "best {product} for daily use",
    "{product} reviews",
    "top rated {product}",
    "{product} with good battery life",
    "stylish {color} {product}",
    "{product} for gifting",
    "durable {product}",
    "affordable {product}",
    "budget {product}",
    "cheap {product}",
    "{product} on sale",
    "trending {product}",
    "new arrivals {product}",
    "{product} with warranty",
    "comfortable {product}",
    "{color} {product} for men",
    "{product} for women",
    "lightweight {product}",
    "wireless {product}",
    "portable {product}",
    "waterproof {product}",
]

_NEITHER_WRAPPERS = [
    "{core}",
    "show me {core}",
    "looking for {core}",
    "need {core}",
    "want {core}",
    "any good {core}",
    "do you have {core}",
    "please suggest {core}",
    "i'm interested in {core}",
    "searching for {core}",
]

# ---------------------------------------------------------------------------
# Hand-written long/descriptive templates (natural, multi-clause phrasing)
# ---------------------------------------------------------------------------
_RANGE_LONG = [
    "I've been searching for a {adjective} {product} and I'd like to keep the price somewhere between {min} and {max} if possible",
    "hey, I'm trying to find a {color} {product} but my budget is strictly between {min} and {max}, can you help",
    "could you point me toward a {brand} {product} that falls somewhere in the {min} to {max} price bracket",
    "I don't mind spending a bit but I'd like the {product} to cost between {min} and {max}, nothing more nothing less",
    "my budget for this {product} is flexible, anywhere from {min} up to {max} works fine for me",
    "I've narrowed it down to a {product}, just need something priced between {min} and {max} for my requirements",
    "so I'm shopping around for a {color} {brand} {product}, and honestly {min} to {max} is the sweet spot I'm aiming for",
    "trying to stay within a budget here, looking at {product} options priced between {min} and {max} rupees",
    "not sure what's out there, but I'd like a {adjective} {product} costing somewhere between {min} and {max}",
    "if you've got a {product} priced anywhere from {min} to {max}, that would be perfect for what I need",
    "I want to treat myself to a new {product}, budget wise I'm thinking between {min} and {max}",
    "honestly just need sum {product} that costs like {min} to {max}, nothing fancy",
    "would love a {brand} {product} but only if it falls between {min} and {max}, otherwise its too much",
    "been eyeing a {color} {product} for a while, my price range is {min} to {max} so hoping to find something there",
    "for my new place I need a {product}, budget bracket is somewhere around {min} to {max}",
    "planning to gift someone a {product}, would like to spend between {min} and {max} on it",
    "my final budget for the {product} purchase is fixed between {min} and {max}, please suggest accordingly",
    "looking to upgrade my {product}, comfortable spending anywhere between {min} and {max}",
    "not trying to overspend, just want a {product} that lands between {min} and {max}",
    "could really use a {adjective} {product}, ideally priced from {min} to {max}",
]

_MAX_LONG = [
    "I really don't want to spend more than {max} on a {product}, so please keep it under that",
    "honestly my budget is tight, so anything for a {product} has to stay under {max}",
    "could you find me a {color} {product} that doesn't go past {max}, that's my hard limit",
    "I'm on a strict budget so the {product} needs to be priced at {max} or less, nothing above that",
    "trying not to break the bank here, so a {product} under {max} would be ideal",
    "would love a {brand} {product} but it absolutely cannot exceed {max}",
    "just need sumthing cheap, {product} for under {max} plz, nothing fancy",
    "my max spend on this {product} is {max}, so please don't show me anything pricier",
    "looking for a {adjective} {product}, as long as it doesn't cost more than {max} I'm happy",
    "I'd rather not go over {max} for a {product}, is there anything in that range",
    "keeping this simple, {product} needs to be capped at {max}, no exceptions",
    "not looking to splurge, a {product} priced anywhere under {max} works for me",
    "if the {product} costs more than {max} it's out of my budget completely",
    "want something practical, a {color} {product} that stays well below {max}",
    "my wallet says no more than {max} for this {product}, so please respect that",
    "just need a {product} for cheap, definitely not exceeding {max}",
    "budget conscious shopper here, {product} has to be {max} or under",
    "the {product} has to be affordable, ideally not more than {max}",
    "would appreciate a {brand} {product} recommendation as long as it's under {max}",
    "I'm flexible on features but firm on price, {product} must be below {max}",
]

_MIN_LONG = [
    "I'm looking for something premium, so a {product} priced north of {min} would actually be preferred",
    "don't show me anything cheap, I want a {product} that's not below {min}",
    "honestly quality matters more than price here, so a {product} above {min} is what I'm after",
    "I'd like a {brand} {product} but only if it costs more than {min}, anything cheaper feels low quality",
    "looking for a high end {color} {product}, starting somewhere around {min} and going up",
    "I want a {product} that's priced beyond {min}, budget isn't really a constraint for me",
    "please only show {product} options costing at least {min}, nothing bargain bin",
    "my minimum spend on a {product} is {min}, I don't want anything priced lower than that",
    "I'm after a {adjective} {product} that's priced past {min}, since I care about quality",
    "show me a {product} that's north of {min} in price, I want something that lasts",
    "not interested in cheap stuff, so a {product} higher than {min} is what I need",
    "I'd like a {brand} {product} priced from {min} onward, nothing budget tier please",
    "looking to invest in a good {product}, so anything above {min} works for me",
    "please recommend a {product} that costs {min} or more, I want the better options",
    "I'm willing to pay a premium, a {product} starting at {min} and up is fine",
    "want a {color} {product} that's definitely not under {min} in price",
    "give me options for a {product} priced beyond the {min} mark",
    "looking for something durable, a {product} costing more than {min} would be ideal",
    "I need a {product} that's at minimum {min}, quality over cheapness",
    "show only {product} that start north of {min}, I don't want the cheap ones",
]

_NEITHER_LONG = [
    "I've been meaning to buy a new {product} for a while now, any suggestions that are {adjective} and look good in {color}",
    "just browsing for a {product} right now, nothing specific in mind yet",
    "can you tell me more about the {brand} {product} lineup, curious what's available",
    "my friend recommended a {product}, wondering what options are out there",
    "trying to decide between a few {product} options, what would you suggest",
    "not sure what I'm looking for exactly, just want a good {product} overall",
    "could you walk me through the best {product} choices available right now",
    "I'm redecorating and thinking about getting a {color} {product}, any ideas",
    "what's trending right now in {product}, just curious to see options",
    "need some inspiration, show me a few {adjective} {product} options",
    "my {product} broke down, need to replace it with something similar",
    "shopping around for a {product} as a gift, no particular budget in mind",
    "just exploring the {brand} catalog for {product}, nothing decided yet",
    "want to see what {product} options exist before I decide anything",
    "curious about {product} reviews, what do people usually recommend",
    "planning ahead for next month, thinking about a new {product} eventually",
    "any {product} you'd personally recommend, open to all options",
    "looking to compare a few {product} models before deciding",
    "what would be a solid everyday {product} for general use",
    "just want to see the {color} {brand} {product} catalog for now",
]

# templates whose wording already implies approximation
APPROX_WORDED_TEMPLATES = {
    "anything {adjective} around {max} ish",
    "{product} roughly around {max}",
}


def _build_category(leadins, phrases, long_templates, target):
    combos = []
    seen = set()
    for leadin in leadins:
        for phrase in phrases:
            text = f"{leadin} {phrase}".strip()
            if text not in seen:
                seen.add(text)
                combos.append(text)

    needed_from_combos = target - len(long_templates)
    result = combos[:needed_from_combos] + list(long_templates)

    for text in result:
        if text in seen and text not in combos:
            seen.add(text)
    assert len(set(result)) == len(result), "duplicate template detected"
    assert len(result) == target, f"expected {target} templates, got {len(result)}"
    return result


def _build_neither(core_phrases, wrappers, long_templates, target):
    combos = []
    seen = set()
    for wrapper in wrappers:
        for core in core_phrases:
            text = wrapper.replace("{core}", core).strip()
            if text not in seen:
                seen.add(text)
                combos.append(text)

    needed_from_combos = target - len(long_templates)
    result = combos[:needed_from_combos] + list(long_templates)
    assert len(set(result)) == len(result), "duplicate template detected"
    assert len(result) == target, f"expected {target} templates, got {len(result)}"
    return result


RANGE_TEMPLATES = _build_category(_LEADINS, _RANGE_PHRASES, _RANGE_LONG, 250)
MAX_TEMPLATES = _build_category(_LEADINS, _MAX_PHRASES, _MAX_LONG, 250) + [
    "sumthing under {max} plz",
    "anything {adjective} around {max} ish",
    "{product} roughly around {max}",
    "{product} that won't break the bank over {max}",
]
MIN_TEMPLATES = _build_category(_LEADINS, _MIN_PHRASES, _MIN_LONG, 250)
NEITHER_TEMPLATES = _build_neither(_NEITHER_CORE, _NEITHER_WRAPPERS, _NEITHER_LONG, 250)

# MAX_TEMPLATES gained 4 informal extras above target of 250; trim back down
# while keeping the informal/approx-worded ones (they're intentional coverage).
if len(MAX_TEMPLATES) > 250:
    MAX_TEMPLATES = MAX_TEMPLATES[:246] + MAX_TEMPLATES[-4:]

assert len(RANGE_TEMPLATES) == 250
assert len(MAX_TEMPLATES) == 250
assert len(MIN_TEMPLATES) == 250
assert len(NEITHER_TEMPLATES) == 250
assert len(set(RANGE_TEMPLATES)) == 250
assert len(set(MAX_TEMPLATES)) == 250
assert len(set(MIN_TEMPLATES)) == 250
assert len(set(NEITHER_TEMPLATES)) == 250
