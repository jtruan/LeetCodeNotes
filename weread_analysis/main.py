#!/usr/bin/env python3
"""
微信读书全套分析系统 — 入口脚本

用法:
  # 1. 使用演示数据（无需账号）
  python main.py --demo

  # 2. 使用真实账号（需要 Cookie）
  python main.py --fetch            # 先抓取数据
  python main.py --analyze          # 再生成报告（可离线复用缓存）

  # 3. 一键抓取并分析
  python main.py --fetch --analyze
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))


def main():
    parser = argparse.ArgumentParser(description="微信读书分析系统")
    parser.add_argument("--demo",    action="store_true", help="使用演示数据运行分析")
    parser.add_argument("--fetch",   action="store_true", help="从微信读书抓取真实数据")
    parser.add_argument("--analyze", action="store_true", help="使用缓存数据生成报告")
    args = parser.parse_args()

    if not any([args.demo, args.fetch, args.analyze]):
        parser.print_help()
        print("\n提示: 运行 `python main.py --demo` 体验演示效果")
        sys.exit(0)

    if args.demo:
        print("🎮 演示模式：生成随机阅读数据...")
        from generate_demo import generate
        generate()
        from weread_api import load_cached
        from analyzer import run_analysis
        data = load_cached()
        paths = run_analysis(data)
        _print_summary(paths)
        return

    if args.fetch:
        from config import WEREAD_COOKIE
        if not WEREAD_COOKIE:
            print("❌ 未设置 Cookie！")
            print("   请在 weread_analysis/.env 中添加：")
            print("   WEREAD_COOKIE=你从浏览器复制的 cookie 字符串")
            sys.exit(1)
        from weread_api import WeReadAPI
        api  = WeReadAPI()
        data = api.fetch_all()
    else:
        from weread_api import load_cached
        data = load_cached()
        if not data["books"]:
            print("⚠️  缓存为空，请先运行 --fetch 或 --demo")
            sys.exit(1)

    if args.analyze or args.fetch:
        from analyzer import run_analysis
        paths = run_analysis(data)
        _print_summary(paths)


def _print_summary(paths):
    print("\n" + "=" * 50)
    print("  生成文件清单")
    print("=" * 50)
    for p in paths:
        print(f"  📄 {p}")
    print("\n使用图片查看器打开 output/ 目录查看图表。")


if __name__ == "__main__":
    main()
