#!/usr/bin/env python3
"""Random choice utility using Python's random module (PRNG).

Not suitable for cryptographic use, fair lotteries, or security-sensitive tasks.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys


def parse_weighted(items: list[str]) -> list[tuple[str, float]]:
    """Parse weighted items in format 'item:weight'."""
    result: list[tuple[str, float]] = []
    for item in items:
        if ':' not in item:
            print(f"Error: weighted item must be in format 'item:weight', got: {item}", file=sys.stderr)
            sys.exit(1)

        choice, weight_str = item.rsplit(':', 1)
        try:
            weight = float(weight_str)
        except ValueError:
            print(f"Error: weight must be a number, got: {weight_str}", file=sys.stderr)
            sys.exit(1)

        if not math.isfinite(weight):
            print(f"Error: weight must be finite, got: {weight}", file=sys.stderr)
            sys.exit(1)

        if weight < 0:
            print(f"Error: weight must be non-negative, got: {weight}", file=sys.stderr)
            sys.exit(1)

        result.append((choice, weight))

    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Random choice using Python's random module (PRNG). "
                    "Not for cryptographic use, fair lotteries, or security-sensitive tasks."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--uniform', nargs='+', metavar='ITEM',
                      help='Uniform random choice among items')
    mode.add_argument('--weighted', nargs='+', metavar='ITEM:WEIGHT',
                      help='Weighted random choice (format: item:weight)')
    parser.add_argument('--json', action='store_true',
                        help='Output result as JSON')

    args = parser.parse_args()

    if args.uniform:
        selected = random.choice(args.uniform)

        if args.json:
            print(json.dumps({
                "mode": "uniform",
                "items": args.uniform,
                "selected": selected,
                "method": "python random module",
            }))
        else:
            print(selected)
        return

    weighted_items = parse_weighted(args.weighted)
    choices = [item for item, _ in weighted_items]
    weights = [weight for _, weight in weighted_items]

    total_weight = sum(weights)
    if not math.isfinite(total_weight):
        print("Error: total weight is not finite", file=sys.stderr)
        sys.exit(1)
    if total_weight <= 0:
        print("Error: total weight must be greater than zero", file=sys.stderr)
        sys.exit(1)

    selected = random.choices(choices, weights=weights, k=1)[0]

    if args.json:
        print(json.dumps({
            "mode": "weighted",
            "items": [{"item": c, "weight": w} for c, w in weighted_items],
            "selected": selected,
            "method": "python random module",
        }))
    else:
        print(selected)


if __name__ == '__main__':
    main()
