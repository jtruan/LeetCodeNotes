"""
微信读书配置文件

使用方法:
1. 浏览器打开 https://weread.qq.com 并登录
2. 按 F12 打开开发者工具 → Network → 找任意请求 → 复制 Cookie 字符串
3. 将 Cookie 写入 .env 文件: WEREAD_COOKIE=你的cookie
   或直接在下面修改 WEREAD_COOKIE 变量
"""

import os
from dotenv import load_dotenv

load_dotenv()

WEREAD_COOKIE = os.getenv("WEREAD_COOKIE", "")

WEREAD_BASE_URL = "https://weread.qq.com"

WEREAD_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://weread.qq.com/",
}

# API 端点
API = {
    "shelf_sync":      "/web/shelf/sync",
    "read_history":    "/web/book/readHistory",
    "bookmarks":       "/web/bookmark/list",
    "reviews":         "/web/review/list",
    "book_info":       "/web/book/info",
    "read_detail":     "/web/book/read",
    "notebook_list":   "/web/user/notebooks",
    "best_highlight":  "/web/book/bestbookmarks",
}

# 输出目录
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
DATA_DIR   = os.path.join(os.path.dirname(__file__), "data")
