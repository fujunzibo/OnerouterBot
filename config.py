import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


def _env_bool(key: str, default: bool) -> bool:
    raw = os.environ.get(key, "").strip().lower()
    if not raw:
        return default
    return raw in ("1", "true", "yes", "on")


BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
PAYMENT_PROVIDER_TOKEN = os.environ.get("PAYMENT_PROVIDER_TOKEN", "").strip()
ADMIN_IDS = {
    int(x.strip())
    for x in os.environ.get("ADMIN_IDS", "").split(",")
    if x.strip().isdigit()
}

ROOT = Path(__file__).resolve().parent
DATABASE_PATH = Path(os.environ.get("DATABASE_PATH", str(ROOT / "data" / "bot.db")))

# 直连 Telegram：设为 0 可禁止读取系统 HTTPS_PROXY/ALL_PROXY（代理坏了会导致 ConnectTimeout）
TELEGRAM_TRUST_ENV = _env_bool("TELEGRAM_TRUST_ENV", True)
# 显式代理，例如 http://127.0.0.1:7890 或 socks5://127.0.0.1:7890（socks 需 pip install "python-telegram-bot[socks]"）
TELEGRAM_PROXY: Optional[str] = os.environ.get("TELEGRAM_PROXY", "").strip() or None


def create_telegram_http_request():
    """配置 httpx：超时、可选代理、可选关闭 trust_env（避免误用系统代理）。"""
    from telegram.request import HTTPXRequest

    httpx_kwargs = {}
    if not TELEGRAM_TRUST_ENV:
        httpx_kwargs["trust_env"] = False

    return HTTPXRequest(
        connection_pool_size=256,
        connect_timeout=30.0,
        read_timeout=30.0,
        write_timeout=30.0,
        pool_timeout=10.0,
        proxy=TELEGRAM_PROXY,
        httpx_kwargs=httpx_kwargs or None,
    )


# 支持的美元面值（与数据库 face_value_usd、菜单一致）
FACE_VALUE_USD = (10, 20, 50, 100, 1000)

# 商品：币种 XTR = Telegram Stars；文案见 i18n.py；price_stars 自行调整
PRODUCTS = {
    "card_10": {
        "payload": "card_10",
        "currency": "XTR",
        "price_stars": 80,
        "face_value_usd": 10,
    },
    "card_20": {
        "payload": "card_20",
        "currency": "XTR",
        "price_stars": 150,
        "face_value_usd": 20,
    },
    "card_50": {
        "payload": "card_50",
        "currency": "XTR",
        "price_stars": 350,
        "face_value_usd": 50,
    },
    "card_100": {
        "payload": "card_100",
        "currency": "XTR",
        "price_stars": 650,
        "face_value_usd": 100,
    },
    "card_1000": {
        "payload": "card_1000",
        "currency": "XTR",
        "price_stars": 5500,
        "face_value_usd": 1000,
    },
}
