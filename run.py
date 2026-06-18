#!/usr/bin/env python3
from src.aggregator import run_all
from src.site_generator import generate_site


def main():
    print("=" * 50)
    print("  AI News Hub - Starting collection...")
    print("=" * 50)
    run_all()
    print("\n" + "=" * 50)
    print("  Generating site...")
    print("=" * 50)
    path = generate_site()
    print(f"\n✅ Done! Open: {path}")


if __name__ == "__main__":
    main()
