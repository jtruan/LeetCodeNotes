"""微信读书 API 封装 — 负责所有数据获取"""

import json
import time
import os
import requests
from config import WEREAD_BASE_URL, WEREAD_HEADERS, WEREAD_COOKIE, API, DATA_DIR


class WeReadAPI:
    def __init__(self, cookie: str = WEREAD_COOKIE):
        if not cookie:
            raise ValueError(
                "未设置 Cookie。请在 .env 文件中设置 WEREAD_COOKIE，"
                "或在初始化时传入 cookie 参数。"
            )
        self.session = requests.Session()
        self.session.headers.update(WEREAD_HEADERS)
        self.session.headers["Cookie"] = cookie

    def _get(self, endpoint: str, params: dict = None) -> dict:
        url = WEREAD_BASE_URL + endpoint
        resp = self.session.get(url, params=params or {}, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, dict) and data.get("errcode", 0) != 0:
            raise RuntimeError(f"API 错误 [{endpoint}]: {data}")
        return data

    # ── 书架 ──────────────────────────────────────────────────────────────
    def get_shelf(self) -> list[dict]:
        data = self._get(API["shelf_sync"], {"synckey": 0, "teenmode": 0})
        books = data.get("books", [])
        return [b.get("book", b) for b in books]

    # ── 阅读历史 ──────────────────────────────────────────────────────────
    def get_read_history(self, book_id: str) -> list[dict]:
        data = self._get(API["read_history"], {"bookId": book_id})
        return data.get("readHistory", {}).get("updated", [])

    # ── 全局笔记本 ────────────────────────────────────────────────────────
    def get_notebooks(self) -> list[dict]:
        data = self._get(API["notebook_list"])
        return data.get("books", [])

    # ── 书签 / 划线 ───────────────────────────────────────────────────────
    def get_bookmarks(self, book_id: str) -> list[dict]:
        data = self._get(API["bookmarks"], {"bookId": book_id})
        updated = data.get("updated", [])
        return updated

    # ── 想法 / 评论 ───────────────────────────────────────────────────────
    def get_reviews(self, book_id: str) -> list[dict]:
        data = self._get(
            API["reviews"],
            {"bookId": book_id, "listType": 11, "mine": 1, "synckey": 0},
        )
        return data.get("reviews", [])

    # ── 书籍详情 ──────────────────────────────────────────────────────────
    def get_book_info(self, book_id: str) -> dict:
        return self._get(API["book_info"], {"bookId": book_id})

    # ── 批量抓取并缓存 ────────────────────────────────────────────────────
    def fetch_all(self, delay: float = 0.5) -> dict:
        """抓取所有数据并保存到 data/ 目录，返回汇总 dict。"""
        os.makedirs(DATA_DIR, exist_ok=True)
        result = {}

        print("📚 正在获取书架...")
        books = self.get_shelf()
        result["books"] = books
        _save(books, "books.json")
        print(f"  → {len(books)} 本书")

        print("\n📓 正在获取笔记本列表...")
        notebooks = self.get_notebooks()
        result["notebooks"] = notebooks
        _save(notebooks, "notebooks.json")
        print(f"  → {len(notebooks)} 本有笔记")

        book_ids = [b["bookId"] for b in books if b.get("bookId")]
        bookmarks_all, reviews_all, history_all = [], [], []

        print(f"\n🔍 正在逐本抓取划线/笔记/历史（共 {len(book_ids)} 本）...")
        for i, bid in enumerate(book_ids, 1):
            title = next(
                (b.get("title", bid) for b in books if b.get("bookId") == bid), bid
            )
            print(f"  [{i}/{len(book_ids)}] {title}", end="\r")
            try:
                bm = self.get_bookmarks(bid)
                bookmarks_all.extend(bm)
                time.sleep(delay)
                rv = self.get_reviews(bid)
                reviews_all.extend(rv)
                time.sleep(delay)
                hist = self.get_read_history(bid)
                history_all.extend(hist)
                time.sleep(delay)
            except Exception as e:
                print(f"\n  ⚠️  {title}: {e}")

        result["bookmarks"] = bookmarks_all
        result["reviews"]   = reviews_all
        result["history"]   = history_all
        _save(bookmarks_all, "bookmarks.json")
        _save(reviews_all,   "reviews.json")
        _save(history_all,   "history.json")

        print(f"\n✅ 完成！划线 {len(bookmarks_all)} 条，笔记 {len(reviews_all)} 条，"
              f"阅读记录 {len(history_all)} 条")
        return result


def _save(obj, filename: str):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def load_cached() -> dict:
    """从本地缓存加载数据（无需 Cookie）。"""
    result = {}
    for name in ("books", "bookmarks", "reviews", "history", "notebooks"):
        path = os.path.join(DATA_DIR, f"{name}.json")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                result[name] = json.load(f)
        else:
            result[name] = []
    return result
