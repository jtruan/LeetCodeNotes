"""
微信读书配置

使用方法:
1. 打开微信读书 App → 我 → 开放能力（或通过官方渠道申请）获取 API Key
2. 将 API Key 写入 .env 文件：WEREAD_API_KEY=wrk-xxxxxxxx
   或直接 export WEREAD_API_KEY=wrk-xxxxxxxx
"""

import os
from dotenv import load_dotenv

load_dotenv()

WEREAD_API_KEY     = os.getenv("WEREAD_API_KEY", "")
WEREAD_GATEWAY_URL = "https://i.weread.qq.com/api/agent/gateway"
SKILL_VERSION      = "1.0.3"

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
DATA_DIR   = os.path.join(os.path.dirname(__file__), "data")
