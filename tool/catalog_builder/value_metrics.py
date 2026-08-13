"""Per-SKU derived value metrics — Catalog Builder Implementation Design
Part 5. Two pure functions, no I/O, no side effects, matching
`Sku.costPerLitre`/`Sku.costPerMlAlcohol`'s own doc comments exactly
(`lib/shared_domain/sku.dart`).
"""

from __future__ import annotations


def cost_per_litre(price: float, size_ml: int) -> float:
    """Price per litre, from `price` and `size_ml`."""
    return price / (size_ml / 1000)


def cost_per_ml_alcohol(price: float, size_ml: int, abv: float) -> float:
    """Price per millilitre of pure alcohol, from `price`, `size_ml`, and
    `abv` (a percentage, e.g. `4.8` for 4.8%). This is the primary axis
    Value Score is computed from."""
    ml_of_alcohol = size_ml * (abv / 100)
    return price / ml_of_alcohol
