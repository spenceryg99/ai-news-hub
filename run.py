#!/usr/bin/env python3
import os
from src.aggregator import run_all, list_dates
from src.site_generator import generate_site


def main():
    print("=" * 50)
    print("  AI News Hub")
    print("=" * 50)

    # Show existing archives
    dates = list_dates()
    if dates:
        print(f"  Existing archives: {len(dates)} days ({dates[0]} ~ {dates[-1]})")
    else:
        print("  No existing archives, starting fresh")

    print("\n" + "-" * 30)
    print("  Collection phase")
    print("-" * 30)
    run_all()

    print("\n" + "-" * 30)
    print("  Site generation phase")
    print("-" * 30)
    path = generate_site()

    print(f"\n✅ Done! Open: {path}")
    print(f"   Total archive days: {len(list_dates())}")


if __name__ == "__main__":
    main()
