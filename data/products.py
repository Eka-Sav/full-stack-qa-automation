import random


class Category:
    SERVICE = "service"
    TRAVEL = "travel"
    GOODS = "goods"


class PriceRange:
    LOW = (10, 100)
    MID = (100, 300)
    HIGH = (300, 600)


# a fixed seed keeps prices "random" but identical on every run,
# so a failed test can be reproduced with the same data
_rng = random.Random(42)


def _price(price_range: tuple[int, int]) -> float:
    return round(_rng.uniform(*price_range), 2)


PRODUCTS = [
    {
        "name": "Cloud Storage",
        "description": "Secure cloud storage for your files.",
        "price": _price(PriceRange.LOW),
        "category": Category.SERVICE,
    },
    {
        "name": "Tech Support",
        "description": "24/7 technical support service.",
        "price": _price(PriceRange.MID),
        "category": Category.SERVICE,
    },
    {
        "name": "City Tour",
        "description": "Guided city tour with local expert.",
        "price": _price(PriceRange.MID),
        "category": Category.TRAVEL,
    },
    {
        "name": "Flight Insurance",
        "description": "Coverage for flight cancellations.",
        "price": _price(PriceRange.HIGH),
        "category": Category.TRAVEL,
    },
    {
        "name": "Office Chair",
        "description": "Ergonomic chair for home office.",
        "price": _price(PriceRange.MID),
        "category": Category.GOODS,
    },
    {
        "name": "Wireless Mouse",
        "description": "Compact wireless mouse.",
        "price": _price(PriceRange.LOW),
        "category": Category.GOODS,
    },
]
