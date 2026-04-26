#!/usr/bin/env python3
"""Random choice utility using Python's random module (PRNG).

Not suitable for cryptographic use, fair lotteries, or security-sensitive tasks.
"""
import argparse
import json
import random
import sys
from typing import List, Tuple


def parse_weighted(items: List[str]) -> List[Tuple[str, float]]:
    """Parse weighted items in format 'item:weight'."""
    result = []
    for item in items:
        if ':' not in item:
            print(f"Error: weighted item must be in format 'item:weight', got: {item}", file=sys.stderr)
            sys.exit(1)
        
        parts = item.rsplit(':', 1)
        if len(parts) != 2:
            print(f"Error: malformed weighted item: {item}", file=sys.stderr)
            sys.exit(1)
        
        choice, weight_str = parts
        try:
            weight = float(weight_str)
        except ValueError:
            print(f"Error: weight must be a number, got: {weight_str}", file=sys.stderr)
            sys.exit(1)
        
        if weight < 0:
            print(f"Error: weight must be non-negative, got: {weight}", file=sys.stderr)
            sys.exit(1)
        
        if not (weight == 0 or (weight > 0 and weight < float('inf'))):
            print(f"Error: weight must be finite, got: {weight}", file=sys.stderr)
            sys.exit(1)
        
        result.append((choice, weight))
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Random choice using Python's random module (PRNG). "
                    "Not for cryptographic use, fair lotteries, or security-sensitive tasks."
    )
    parser.add_argument('--uniform', nargs='+', metavar='ITEM',
                        help='Uniform random choice among items')
    parser.add_argument('--weighted', nargs='+', metavar='ITEM:WEIGHT',
                        help='Weighted random choice (format: item:weight)')
    parser.add_argument('--json', action='store_true',
                        help='Output result as JSON')
    
    args = parser.parse_args()
    
    if args.uniform and args.weighted:
        print("Error: cannot use both --uniform and --weighted", file=sys.stderr)
        sys.exit(1)
    
    if not args.uniform and not args.weighted:
        parser.print_help()
        sys.exit(1)
    
    if args.uniform:
        if not args.uniform:
            print("Error: --uniform requires at least one item", file=sys.stderr)
            sys.exit(1)
        
        selected = random.choice(args.uniform)
        
        if args.json:
            print(json.dumps({
                "mode": "uniform",
                "selected": selected,
                "method": "python random module"
            }))
        else:
            print(selected)
    
    elif args.weighted:
        if not args.weighted:
            print("Error: --weighted requires at least one item", file=sys.stderr)
            sys.exit(1)
        
        weighted_items = parse_weighted(args.weighted)
        choices = [item for item, _ in weighted_items]
        weights = [weight for _, weight in weighted_items]
        
        total_weight = sum(weights)
        if total_weight <= 0:
            print("Error: total weight must be greater than zero", file=sys.stderr)
            sys.exit(1)
        
        selected = random.choices(choices, weights=weights, k=1)[0]
        
        if args.json:
            print(json.dumps({
                "mode": "weighted",
                "selected": selected,
                "method": "python random module"
            }))
        else:
            print(selected)


if __name__ == '__main__':
    main()
