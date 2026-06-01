"""
微信读书 API 封装 — 使用官方 Agent API Gateway
鉴权: Authorization: Bearer $WEREAD_API_KEY (格式 wrk-xxxxxxxx)
"""

import json
import os
import time
import requests
from config import WEREAD_API_KEY, WEREAD_GATEWAY_URL, SKILL_VERSION, DATA_DIR


class WeReadAPI:
    def __init__(self, api_key: str = WEREAD_API_KEY):
        if not api_key:
            raise ValueError(
                "未设置 WEREAD_API_KEY。\n"
                "请在 weread_analysis/.env 中添加：WEREAD_API_KEY=wrk-xxxxxxxx\n"
                "或运行：export WEREAD_API_KEY=wrk-xxxxxxxx"
            )
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization":  f"Bearer {api_key}",
            "Content-Type":   "application/json",
            "User-Agent":     "WeRead/7.0 (skill-client/1.0)",
        })

    def _post(self, api_name: str, **params) -> dict:
        body = {"api_name": api_name, "skill_version": SKILL_VERSION, **params}
        resp = self.session.post(WEREAD_GATEWAY_URL, json=body, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, dict):
            if data.get("errcode", 0) != 0:
                raise RuntimeError(f"API 错误 [{api_name}]: {data.get('errmsg', data)}")
            if "upgrade_info" in data:
                raise RuntimeError(
                    f"Skill 需要升级：{data['upgrade_info'].get('message', '')}\n"
                    "请运行：npx skills add Tencent/WeChatReading -g"
                )
        return data

    # ── 书架 ──────────────────────────────────────────────────────────────
    def get_shelf(self) -> dict:
        """返回 {books: [...], albums: [...], mp: {...}}"""
        return self._post("/shelf/sync")

    # ── 阅读统计 ──────────────────────────────────────────────────────────
    def get_readdata(self, mode: str = "monthly", base_time: int = 0) -> dict:
        """
        mode: weekly / monthly / annually / overall
        base_time: Unix 时间戳，0 = 当前周期
        """
        kwargs = {"mode": mode}
        if base_time:
            kwargs["baseTime"] = base_time
        return self._post("/readdata/detail", **kwargs)

    # ── 笔记本列表 ────────────────────────────────────────────────────────
    def get_notebooks(self, count: int = 100) -> dict:
        return self._post("/user/notebooks", count=count)

    # ── 划线列表 ──────────────────────────────────────────────────────────
    def get_bookmarks(self, book_id: str) -> dict:
        return self._post("/book/bookmarklist", bookId=book_id)

    # ── 我的想法/点评 ─────────────────────────────────────────────────────
    def get_my_reviews(self, book_id: str) -> dict:
        return self._post("/review/list/mine", bookId=book_id)

    # ── 书籍信息 ──────────────────────────────────────────────────────────
    def get_book_info(self, book_id: str) -> dict:
        return self._post("/book/info", bookId=book_id)

    # ── 阅读进度 ──────────────────────────────────────────────────────────
    def get_progress(self, book_id: str) -> dict:
        return self._post("/book/getprogress", bookId=book_id)

    # ── 搜索 ──────────────────────────────────────────────────────────────
    def search(self, keyword: str, count: int = 10) -> dict:
        return self._post("/store/search", keyword=keyword, count=count)

    # ── 推荐 ──────────────────────────────────────────────────────────────
    def recommend(self, count: int = 12) -> dict:
        return self._post("/book/recommend", count=count)

    # ── 列出所有接口 ──────────────────────────────────────────────────────
    def list_apis(self) -> dict:
        return self._post("/_list")

    # ── 批量抓取并缓存 ────────────────────────────────────────────────────
    def fetch_all(self, delay: float = 0.5) -> dict:
        """抓取所有关键数据，保存到 data/ 目录，返回汇总 dict。"""
        os.makedirs(DATA_DIR, exist_ok=True)
        result = {}

        # 书架
        print("📚 正在获取书架...")
        shelf = self.get_shelf()
        books   = shelf.get("books", [])
        albums  = shelf.get("albums", [])
        result["books"]  = books
        result["albums"] = albums
        _save(shelf, "shelf.json")
        print(f"  → 电子书 {len(books)} 本，有声书 {len(albums)} 本")

        # 总体阅读统计
        print("\n📊 正在获取阅读统计（总计 / 本年 / 本月）...")
        for mode in ("overall", "annually", "monthly"):
            rd = self.get_readdata(mode=mode)
            result[f"readdata_{mode}"] = rd
            _save(rd, f"readdata_{mode}.json")
            time.sleep(delay)

        # 笔记本
        print("\n📓 正在获取笔记本列表...")
        nb = self.get_notebooks()
        result["notebooks"] = nb.get("books", [])
        _save(nb, "notebooks.json")
        print(f"  → {len(result['notebooks'])} 本有笔记")

        # 逐书获取划线 + 想法
        book_ids = [b["bookId"] for b in books if b.get("bookId")]
        bookmarks_all, reviews_all = [], []
        print(f"\n🔍 正在抓取划线/想法（共 {len(book_ids)} 本）...")
        for i, bid in enumerate(book_ids, 1):
            title = next((b.get("title", bid) for b in books if b.get("bookId") == bid), bid)
            print(f"  [{i}/{len(book_ids)}] {title}", end="\r")
            try:
                bm = self.get_bookmarks(bid)
                bookmarks_all.extend(bm.get("updated", []))
                time.sleep(delay)
                rv = self.get_my_reviews(bid)
                reviews_all.extend(rv.get("reviews", []))
                time.sleep(delay)
            except Exception as e:
                print(f"\n  ⚠️  {title}: {e}")

        result["bookmarks"] = bookmarks_all
        result["reviews"]   = reviews_all
        _save(bookmarks_all, "bookmarks.json")
        _save(reviews_all,   "reviews.json")

        print(f"\n✅ 完成！划线 {len(bookmarks_all)} 条，想法 {len(reviews_all)} 条")
        return result


def _save(obj, filename: str):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def load_cached() -> dict:
    """从本地缓存加载数据（可离线使用）。"""
    result = {}
    for name in ("books", "albums", "bookmarks", "reviews", "notebooks"):
        path = os.path.join(DATA_DIR, f"{name}.json")
        result[name] = _load_json(path) if os.path.exists(path) else []
    for mode in ("overall", "annually", "monthly"):
        path = os.path.join(DATA_DIR, f"readdata_{mode}.json")
        result[f"readdata_{mode}"] = _load_json(path) if os.path.exists(path) else {}
    return result


def _load_json(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)
