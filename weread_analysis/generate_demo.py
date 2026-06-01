"""
生成演示数据并运行分析 — 无需真实账号即可体验完整功能。
用法: python generate_demo.py
"""

import json
import os
import random
from datetime import datetime, timedelta
from config import DATA_DIR

random.seed(42)

BOOKS = [
    ("book001", "人类简史",      "历史"),
    ("book002", "思考，快与慢",   "心理学"),
    ("book003", "原则",          "管理"),
    ("book004", "穷查理宝典",     "商业"),
    ("book005", "活着",          "文学"),
    ("book006", "三体",          "科幻"),
    ("book007", "毛泽东传",       "传记"),
    ("book008", "深度工作",       "效率"),
    ("book009", "刻意练习",       "效率"),
    ("book010", "被讨厌的勇气",   "心理学"),
    ("book011", "纳瓦尔宝典",     "商业"),
    ("book012", "如何阅读一本书", "方法论"),
    ("book013", "零售的哲学",     "商业"),
    ("book014", "影响力",         "心理学"),
    ("book015", "苏东坡传",       "传记"),
]

HIGHLIGHTS = [
    "人类的历史是一个不断超越自身局限的故事。",
    "系统1是直觉式的、快速的；系统2是分析式的、缓慢的。",
    "痛苦＋反思＝进步。",
    "投资最重要的事是不要亏损。",
    "人是为活着本身而活着的，而不是为活着之外的任何事物所活着。",
    "宇宙的熵是不断增加的。",
    "时间是最稀缺的资源，必须有意识地管理。",
    "深度工作是在无干扰状态下进行的专注性职业活动。",
    "刻意练习是有目的的练习，而不是机械重复。",
    "课题分离是一切人际关系烦恼的解决之道。",
    "财富是你睡着时仍在为你赚钱的东西。",
    "带着问题去读书，才能从书中获得真正的收益。",
    "零售的本质是提供价值，而非单纯的商品交换。",
    "顺从是一种强大的影响力武器，它绕过了理性思考。",
    "乐观是宋代文人的精神底色。",
    "认知偏差往往让我们做出次优决策。",
    "复利的力量在于时间的长度，而非单次的收益率。",
    "专注比努力更重要，方向比速度更关键。",
    "大脑天生懒惰，只有系统训练才能改变默认模式。",
    "真正的自由来自于内心的独立，而非外在的条件。",
]

NOTES = [
    "这个观点很有启发性，结合自身经历来看确实如此。",
    "需要在实际工作中验证这个方法论是否适用。",
    "和之前读的《刻意练习》里的观点形成了呼应。",
    "这段话可以当作座右铭，时常回味。",
    "作者对这个问题的分析太深刻了，值得反复读。",
    "联系到最近经历的一件事，理解更深了。",
]


def _ts(days_ago: int, hour_offset: int = 0) -> int:
    t = datetime.now() - timedelta(days=days_ago, hours=-hour_offset)
    return int(t.timestamp())


def generate():
    os.makedirs(DATA_DIR, exist_ok=True)

    # ── 书架 ──────────────────────────────────────────────────────────────
    books = []
    for bid, title, cat in BOOKS:
        books.append({
            "bookId":       bid,
            "title":        title,
            "category":     cat,
            "finishReading": random.choice([1, 1, 0]),
            "cover":        "",
            "author":       "作者" + bid[-3:],
        })
    _dump(books, "books.json")

    # ── 阅读历史（近 365 天，随机选 200 天阅读）──────────────────────────
    history = []
    active_days = sorted(random.sample(range(365), 220))
    for d in active_days:
        n_sessions = random.randint(1, 3)
        for _ in range(n_sessions):
            bid = random.choice(BOOKS)[0]
            history.append({
                "bookId":   bid,
                "readDate": _ts(365 - d),
                "readTime": random.randint(5 * 60, 90 * 60),
            })
    _dump(history, "history.json")

    # ── 划线 ──────────────────────────────────────────────────────────────
    bookmarks = []
    for i in range(350):
        bid  = random.choice(BOOKS)[0]
        text = random.choice(HIGHLIGHTS)
        bookmarks.append({
            "bookId":   bid,
            "markText": text,
            "createTime": _ts(random.randint(0, 365)),
            "style":    random.randint(0, 3),
        })
    _dump(bookmarks, "bookmarks.json")

    # ── 笔记 ──────────────────────────────────────────────────────────────
    reviews = []
    for i in range(80):
        bid  = random.choice(BOOKS)[0]
        note = random.choice(NOTES)
        reviews.append({
            "review": {
                "bookId":     bid,
                "content":    note,
                "createTime": _ts(random.randint(0, 365)),
            }
        })
    _dump(reviews, "reviews.json")

    # ── 笔记本（与书架相同结构）─────────────────────────────────────────
    notebooks = [{"bookId": bid, "title": title} for bid, title, _ in BOOKS[:10]]
    _dump(notebooks, "notebooks.json")

    print(f"✅ 演示数据已生成到 {DATA_DIR}/")


def _dump(obj, name):
    with open(os.path.join(DATA_DIR, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    generate()
