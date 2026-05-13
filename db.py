import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator, Iterable, Optional

from config import DATABASE_PATH, FACE_VALUE_USD

_lock = threading.Lock()
_VALID_FACE = frozenset(FACE_VALUE_USD)


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _migrate_tokens(conn: sqlite3.Connection) -> None:
    rows = conn.execute("PRAGMA table_info(tokens)").fetchall()
    if not rows:
        return
    colnames = {r[1] for r in rows}
    if "face_value_usd" not in colnames:
        conn.execute(
            "ALTER TABLE tokens ADD COLUMN face_value_usd INTEGER NOT NULL DEFAULT 10"
        )


def init_db() -> None:
    _ensure_parent(DATABASE_PATH)
    with _connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token TEXT NOT NULL UNIQUE,
                face_value_usd INTEGER NOT NULL DEFAULT 10,
                sold INTEGER NOT NULL DEFAULT 0,
                sold_to_user_id INTEGER,
                sold_order_id TEXT,
                sold_at TEXT
            );

            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_payment_charge_id TEXT UNIQUE,
                provider_payment_charge_id TEXT,
                user_id INTEGER NOT NULL,
                username TEXT,
                product_payload TEXT NOT NULL,
                amount INTEGER NOT NULL,
                currency TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                fulfilled_at TEXT
            );

            CREATE TABLE IF NOT EXISTS user_settings (
                user_id INTEGER PRIMARY KEY NOT NULL,
                locale TEXT NOT NULL DEFAULT 'en'
            );
            """
        )
        _migrate_tokens(conn)
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_tokens_available_denom
            ON tokens(face_value_usd, sold) WHERE sold = 0
            """
        )
        conn.commit()


@contextmanager
def _connect() -> Generator[sqlite3.Connection, None, None]:
    with _lock:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    try:
        conn.row_factory = sqlite3.Row
        yield conn
    finally:
        conn.close()


def _parse_face_token_line(line: str) -> Optional[tuple[int, str]]:
    line = line.strip()
    if not line or "," not in line:
        return None
    left, right = line.split(",", 1)
    left = left.strip().lstrip("$").strip()
    try:
        face = int(left)
    except ValueError:
        return None
    if face not in _VALID_FACE:
        return None
    token = right.strip()
    if not token:
        return None
    return (face, token)


def add_tokens(lines: Iterable[str]) -> int:
    """导入未售卡密。每行格式：面值,卡密（面值仅可为 10 / 20 / 50 / 100 / 1000，可带 $）。"""
    n = 0
    with _connect() as conn:
        for line in lines:
            parsed = _parse_face_token_line(line)
            if not parsed:
                continue
            face, token = parsed
            try:
                conn.execute(
                    "INSERT INTO tokens (token, face_value_usd) VALUES (?, ?)",
                    (token, face),
                )
                n += 1
            except sqlite3.IntegrityError:
                continue
        conn.commit()
    return n


def count_available_for_face(face_value_usd: int) -> int:
    if face_value_usd not in _VALID_FACE:
        return 0
    with _connect() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS c FROM tokens WHERE sold = 0 AND face_value_usd = ?",
            (face_value_usd,),
        ).fetchone()
        return int(row["c"]) if row else 0


def count_available_tokens() -> int:
    """全部未售张数（各面值合计）。"""
    with _connect() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS c FROM tokens WHERE sold = 0"
        ).fetchone()
        return int(row["c"]) if row else 0


def stock_counts_by_face() -> dict[int, int]:
    """各面值未售张数。"""
    out: dict[int, int] = {}
    with _connect() as conn:
        for fv in FACE_VALUE_USD:
            row = conn.execute(
                "SELECT COUNT(*) AS c FROM tokens WHERE sold = 0 AND face_value_usd = ?",
                (fv,),
            ).fetchone()
            out[fv] = int(row["c"]) if row else 0
    return out


def get_locale(user_id: int) -> Optional[str]:
    with _connect() as conn:
        row = conn.execute(
            "SELECT locale FROM user_settings WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        return str(row["locale"]) if row else None


def set_locale(user_id: int, locale: str) -> None:
    from i18n import DEFAULT_LOCALE, SUPPORTED_LOCALES

    if locale not in SUPPORTED_LOCALES:
        locale = DEFAULT_LOCALE
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO user_settings (user_id, locale) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET locale = excluded.locale
            """,
            (user_id, locale),
        )
        conn.commit()


def ensure_locale_row(user_id: int, telegram_language_code: Optional[str]) -> str:
    """首次出现时根据 Telegram 客户端语言写入偏好（默认 en，阿拉伯客户端为 ar）。"""
    existing = get_locale(user_id)
    if existing:
        from i18n import DEFAULT_LOCALE, SUPPORTED_LOCALES

        return existing if existing in SUPPORTED_LOCALES else DEFAULT_LOCALE
    from i18n import normalize_telegram_language

    guessed = normalize_telegram_language(telegram_language_code)
    set_locale(user_id, guessed)
    return guessed


def face_value_from_payload(product_payload: str) -> Optional[int]:
    if not product_payload.startswith("card_"):
        return None
    try:
        v = int(product_payload[5:])
    except ValueError:
        return None
    if v not in _VALID_FACE:
        return None
    return v


def fulfill_order(
    user_id: int,
    product_payload: str,
    telegram_payment_charge_id: Optional[str],
    provider_payment_charge_id: Optional[str],
    amount: int,
    currency: str,
    username: Optional[str],
) -> tuple[str, list[str]]:
    """
    记录订单并发货：按面值取 1 张未售卡。
    返回 (order_id_str, list_of_codes_for_user).
    """
    face = face_value_from_payload(product_payload)
    if face is None:
        raise RuntimeError("invalid_product")

    tokens: list[str] = []

    with _connect() as conn:
        conn.execute("BEGIN IMMEDIATE")
        rows = conn.execute(
            """
            SELECT id, token FROM tokens
            WHERE sold = 0 AND face_value_usd = ?
            ORDER BY id LIMIT 1
            """,
            (face,),
        ).fetchall()
        if len(rows) < 1:
            conn.rollback()
            raise RuntimeError("insufficient_stock")

        order_id: Optional[int] = None
        if telegram_payment_charge_id:
            cur = conn.execute(
                """
                INSERT INTO orders (
                    telegram_payment_charge_id, provider_payment_charge_id,
                    user_id, username, product_payload, amount, currency, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'paid')
                """,
                (
                    telegram_payment_charge_id,
                    provider_payment_charge_id,
                    user_id,
                    username,
                    product_payload,
                    amount,
                    currency,
                ),
            )
            order_id = cur.lastrowid
        else:
            cur = conn.execute(
                """
                INSERT INTO orders (
                    telegram_payment_charge_id, provider_payment_charge_id,
                    user_id, username, product_payload, amount, currency, status
                ) VALUES (NULL, NULL, ?, ?, ?, ?, ?, 'paid')
                """,
                (user_id, username, product_payload, amount, currency),
            )
            order_id = cur.lastrowid

        now = datetime.now(timezone.utc).isoformat()
        oid_str = str(order_id)

        for r in rows:
            conn.execute(
                """
                UPDATE tokens SET sold = 1, sold_to_user_id = ?, sold_order_id = ?, sold_at = ?
                WHERE id = ?
                """,
                (user_id, oid_str, now, r["id"]),
            )
            tokens.append(r["token"])

        conn.execute(
            "UPDATE orders SET fulfilled_at = ?, status = 'fulfilled' WHERE id = ?",
            (now, order_id),
        )
        conn.commit()

    return (oid_str, tokens)
