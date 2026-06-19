#!/usr/bin/env python3
"""
AI News Hub - 每周 AI 深度分析报告
每日自动采集数据，每周生成主题分类的深度分析。
"""
import os
from src.aggregator import run_all, list_dates
from src.site_generator import generate_site


def main():
    print("=" * 52)
    print("  AI News Hub - \u6bcf\u5468AI\u6df1\u5ea6\u5206\u6790"
          "\n  \u6bcf\u65e5\u91c7\u96c6 \u00b7 \u4e3b\u9898\u8ffd\u8e2a \u00b7 \u5468\u5ea6\u62a5\u544a")
    print("=" * 52)

    dates = list_dates()
    archive_count = len(dates)
    if archive_count > 0:
        print(f"  \u5df2\u6709 {archive_count} \u5929\u7684\u5386\u53f2\u6570\u636e"
              f" ({dates[0]} ~ {dates[-1]})")
    else:
        print("  \u6ca1\u6709\u5386\u53f2\u6570\u636e\uff0c\u4ece\u5934\u5f00\u59cb")

    # Phase 1: Collect
    print("\n" + "-" * 30)
    print("  \u91c7\u96c6\u9636\u6bb5")
    print("-" * 30)
    run_all()

    # Phase 2: Generate weekly report
    print("\n" + "-" * 30)
    print("  \u751f\u6210\u5468\u62a5")
    print("-" * 30)
    path = generate_site()

    print(f"\n\u2705 \u5b8c\u6210\uff01")
    print(f"   \u5468\u62a5: {path}")
    dates = list_dates()
    print(f"   \u5386\u53f2\u6570\u636e: {len(dates)} \u5929")


if __name__ == "__main__":
    main()
