"""
生成演示数据（与官方 API 返回格式一致）并运行分析。
用法: python generate_demo.py
"""

import json
import os
import random
import time
from config import DATA_DIR

random.seed(42)

BOOKS_DATA = [
    ("book001", "人类简史",      "历史",   "尤瓦尔·赫拉利"),
    ("book002", "思考，快与慢",   "心理学", "丹尼尔·卡尼曼"),
    ("book003", "原则",          "管理",   "瑞·达利欧"),
    ("book004", "穷查理宝典",     "商业",   "查理·芒格"),
    ("book005", "活着",          "文学",   "余华"),
    ("book006", "三体",          "科幻",   "刘慈欣"),
    ("book007", "毛泽东传",       "传记",   "罗斯·特里尔"),
    ("book008", "深度工作",       "效率",   "卡尔·纽波特"),
    ("book009", "刻意练习",       "效率",   "安德斯·艾利克森"),
    ("book010", "被讨厌的勇气",   "心理学", "岸见一郎"),
    ("book011", "纳瓦尔宝典",     "商业",   "纳瓦尔·拉维坎特"),
    ("book012", "如何阅读一本书", "方法论", "莫提默·艾德勒"),
    ("book013", "零售的哲学",     "商业",   "铃木敏文"),
    ("book014", "影响力",         "心理学", "罗伯特·西奥迪尼"),
    ("book015", "苏东坡传",       "传记",   "林语堂"),
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

def _ts(days_ago=0):
    return int(time.time()) - days_ago * 86400


def generate():
    os.makedirs(DATA_DIR, exist_ok=True)

    # ── 书架（books 格式对应 /shelf/sync 回包）────────────────────────
    books = [
        {
            "bookId":        bid,
            "title":         title,
            "author":        author,
            "category":      cat,
            "finishReading": random.choice([1, 1, 0]),
            "cover":         "",
            "readUpdateTime": _ts(random.randint(0, 180)),
        }
        for bid, title, cat, author in BOOKS_DATA
    ]
    _dump(books, "books.json")
    _dump([], "albums.json")

    # ── 划线（/book/bookmarklist 回包 updated[]）───────────────────────
    bookmarks = [
        {
            "bookId":     random.choice(BOOKS_DATA)[0],
            "markText":   random.choice(HIGHLIGHTS),
            "createTime": _ts(random.randint(0, 365)),
            "chapterUid": random.randint(1, 30),
            "range":      f"{random.randint(100,900)}-{random.randint(901,2000)}",
            "style":      random.randint(0, 3),
        }
        for _ in range(350)
    ]
    _dump(bookmarks, "bookmarks.json")

    # ── 想法/点评（/review/list/mine 回包 reviews[]）───────────────────
    reviews = [
        {
            "review": {
                "bookId":     random.choice(BOOKS_DATA)[0],
                "content":    random.choice(NOTES),
                "createTime": _ts(random.randint(0, 365)),
                "chapterUid": random.randint(1, 30),
            }
        }
        for _ in range(80)
    ]
    _dump(reviews, "reviews.json")

    # ── 笔记本 ────────────────────────────────────────────────────────
    notebooks = [{"bookId": bid, "title": title} for bid, title, _, __ in BOOKS_DATA[:10]]
    _dump(notebooks, "notebooks.json")

    # ── readdata_overall（模拟 /readdata/detail?mode=overall）───────────
    cat_ids = list({cat for _, _, cat, __ in BOOKS_DATA})
    prefer_category = [
        {
            "categoryId":          i + 1,
            "categoryTitle":       cat,
            "readingTime":         random.randint(3600, 72000),
            "readingCount":        random.randint(1, 5),
            "val":                 round(random.uniform(0.2, 1.0), 2),
            "categoryType":        0,
        }
        for i, cat in enumerate(cat_ids)
    ]
    book_id_list = [b[0] for b in BOOKS_DATA]
    read_longest = [
        {
            "book":     {"bookId": bid, "title": title, "author": author},
            "readTime": random.randint(3600, 36000),
            "tags":     [],
        }
        for bid, title, _, author in random.sample(BOOKS_DATA, 5)
    ]

    prefer_time_raw = [0] * 24
    for h in range(24):
        base = 0
        if 6 <= h <= 8:   base = 1800
        elif 9 <= h <= 11: base = 3600
        elif 12 <= h <= 13: base = 1200
        elif 19 <= h <= 22: base = 4500
        prefer_time_raw[h] = base + random.randint(-300, 300) if base else random.randint(0, 200)
    # preferTime 从 6 点起
    prefer_time = prefer_time_raw[6:] + prefer_time_raw[:6]

    readdata_overall = {
        "totalReadTime":    random.randint(600000, 1200000),
        "readDays":         random.randint(150, 300),
        "preferCategory":   prefer_category,
        "preferTime":       prefer_time,
        "preferTimeWord":   "偏好晚间阅读",
        "preferAuthor":     [
            {"name": author, "count": random.randint(1, 3), "readTime": f"{random.randint(1,8)}小时{random.randint(0,59)}分钟"}
            for _, _, _, author in random.sample(BOOKS_DATA, 5)
        ],
        "readLongest":      read_longest,
        "readStat": [
            {"stat": "读过",  "counts": f"{len(books)}本"},
            {"stat": "读完",  "counts": f"{sum(1 for b in books if b.get('finishReading')==1)}本"},
            {"stat": "笔记",  "counts": f"{len(reviews)}条"},
            {"stat": "划线",  "counts": f"{len(bookmarks)}条"},
        ],
    }
    _dump(readdata_overall, "readdata_overall.json")

    # ── readdata_annually（readTimes 按月分桶）────────────────────────
    import time as _time
    now = int(_time.time())
    read_times = {}
    for m in range(12):
        bucket_ts = now - (11 - m) * 30 * 86400
        read_times[str(bucket_ts)] = random.randint(18000, 144000)
    readdata_annual = {
        "totalReadTime": sum(read_times.values()),
        "readDays":      random.randint(150, 280),
        "readTimes":     read_times,
        "preferCategory": prefer_category,
        "preferTime":     prefer_time,
        "preferTimeWord": "偏好晚间阅读",
    }
    _dump(readdata_annual, "readdata_annually.json")

    _dump({}, "readdata_monthly.json")

    print(f"✅ 演示数据已生成到 {DATA_DIR}/")


def _dump(obj, name):
    with open(os.path.join(DATA_DIR, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    generate()
