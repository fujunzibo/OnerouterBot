"""UI strings: English (default) and Arabic."""

from __future__ import annotations

from typing import Any, Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from config import FACE_VALUE_USD, PRODUCTS

SUPPORTED_LOCALES = ("en", "ar")
DEFAULT_LOCALE = "en"

STRINGS: dict[str, dict[str, str]] = {
    "en": {
        "start.welcome": (
            "This shop sells digital cards in denominations "
            "$10 / $20 / $50 / $100 / $1000.\n"
            "Choose a denomination below. After payment, your code is sent automatically.\n"
            "If the menu disappears, send /start.\n"
            "Language: /lang — English (default) or Arabic."
        ),
        "lang.choose": "Choose your language:",
        "lang.confirm": "You are now using English.",
        "btn.card_10": "$10 card",
        "btn.card_20": "$20 card",
        "btn.card_50": "$50 card",
        "btn.card_100": "$100 card",
        "btn.card_1000": "$1000 card",
        "btn.stock": "Stock",
        "btn.help": "Help",
        "stock.row": "${face}: {count} pcs",
        "stock.total": "Total unsold: {total} pcs",
        "help.body": (
            "1. Tap a denomination, then pay with Telegram Stars.\n"
            "2. After payment, your card code is sent immediately — keep it secret.\n"
            "3. Send /start if the menu is missing.\n"
            "4. For payment issues, contact support (add your contact in the bot description)."
        ),
        "fallback.buttons": "Use the buttons below, or send /start.",
        "err.no_permission": "No permission.",
        "cancel.done": "Cancelled.",
        "restock.prompt": (
            "Send the next message as inventory, one card per line:\n"
            "denomination,code\n"
            "Denomination must be 10, 20, 50, 100, or 1000 (you may use $10). Examples:\n"
            "10,sk-xxxxx\n"
            "1000,CODE-YYYY\n"
            "Send /cancel to abort."
        ),
        "restock.done": "Imported {n} new cards (duplicates skipped).\n\n{summary}",
        "myid": (
            "Your Telegram user ID: `{uid}`\n"
            "Put this number in `ADMIN_IDS` in `.env` on the server, restart the bot, then you can use /restock."
        ),
        "out_of_stock": "${face} is out of stock. Try later or contact the seller.",
        "out_of_stock.admin": (
            "\n\n(Admin) Send /restock, then paste lines as `denomination,code` (e.g. `50,yourcode`). "
            "If you see “no permission”, set `ADMIN_IDS` in `.env` and restart; /myid shows your ID."
        ),
        "pay.need_provider": "This product needs PAYMENT_PROVIDER_TOKEN in `.env` (non-Stars).",
        "checkout.invalid": "Invalid product.",
        "checkout.no_stock": "Out of stock.",
        "pay.success_no_stock": "Payment received but stock ran out. Contact the seller for a refund or restock.\nCharge: {charge}",
        "pay.invalid_product": "Invalid order. Contact the seller.",
        "pay.success": "Payment OK, order #{order}. {label}\n\nCodes (do not share):\n{body}",
        "pay.success_label": "Face value: ${face}",
        "help.message": (
            "🎫 **Card Store Support**\n\n"
            "**How to buy:**\n"
            "1. Click /start or the 🛒 Store button\n"
            "2. Browse available cards\n"
            "3. Select payment method and complete purchase\n"
            "4. Your card codes will be delivered instantly\n\n"
            "**Payment Methods:**\n"
            "- Telegram Wallet Pay\n"
            "- Crypto (USDT/TRC20)\n"
            "- Credit/Debit Card\n\n"
            "**After-sales:**\n"
            "Contact admin for issues: @your_username\n\n"
            "**Commands:**\n"
            "/start - Open store\n"
            "/help - This help message\n"
            "/status - View purchased cards"
        ),
        "status.no_orders": "You have no orders yet. Use /start to browse our store!",
        "status.orders": "📋 Your Orders:\n\n{orders}",
        "product.card_10.title": "Digital card $10",
        "product.card_10.description": "$10 denomination. Code delivered after payment.",
        "product.card_10.invoice_line": "Digital card $10",
        "product.card_20.title": "Digital card $20",
        "product.card_20.description": "$20 denomination. Code delivered after payment.",
        "product.card_20.invoice_line": "Digital card $20",
        "product.card_50.title": "Digital card $50",
        "product.card_50.description": "$50 denomination. Code delivered after payment.",
        "product.card_50.invoice_line": "Digital card $50",
        "product.card_100.title": "Digital card $100",
        "product.card_100.description": "$100 denomination. Code delivered after payment.",
        "product.card_100.invoice_line": "Digital card $100",
        "product.card_1000.title": "Digital card $1000",
        "product.card_1000.description": "$1000 denomination. Code delivered after payment.",
        "product.card_1000.invoice_line": "Digital card $1000",
    },
    "ar": {
        "start.welcome": (
            "المتجر يبيع بطاقات رقمية بفئات: "
            "10$ / 20$ / 50$ / 100$ / 1000$.\n"
            "اختر الفئة من القائمة أدناه. بعد الدفع يُرسل الرمز تلقائياً.\n"
            "إذا اختفت القائمة، أرسل /start.\n"
            "اللغة: /lang — الإنجليزية (الافتراضي) أو العربية."
        ),
        "lang.choose": "اختر اللغة:",
        "lang.confirm": "أنت تستخدم العربية الآن.",
        "btn.card_10": "بطاقة 10$",
        "btn.card_20": "بطاقة 20$",
        "btn.card_50": "بطاقة 50$",
        "btn.card_100": "بطاقة 100$",
        "btn.card_1000": "بطاقة 1000$",
        "btn.stock": "المخزون",
        "btn.help": "مساعدة",
        "stock.row": "{face}$: {count} قطعة",
        "stock.total": "إجمالي غير المباع: {total} قطعة",
        "help.body": (
            "1) اضغط الفئة ثم ادفع بـ Telegram Stars.\n"
            "2) بعد الدفع يُرسل رمز البطاقة فوراً — احفظه ولا تشاركه.\n"
            "3) أرسل /start إذا اختفت القائمة.\n"
            "4) لمشاكل الدفع، تواصل مع الدعم (أضف وسيلة تواصل في وصف البوت)."
        ),
        "fallback.buttons": "استخدم الأزرار أدناه، أو أرسل /start.",
        "err.no_permission": "لا صلاحية.",
        "cancel.done": "تم الإلغاء.",
        "restock.prompt": (
            "أرسل الرسالة التالية كمخزون، سطر لكل بطاقة:\n"
            "الفئة,الرمز\n"
            "الفئة يجب أن تكون 10 أو 20 أو 50 أو 100 أو 1000 (يمكنك كتابة $10). أمثلة:\n"
            "10,sk-xxxxx\n"
            "1000,CODE-YYYY\n"
            "أرسل /cancel للإلغاء."
        ),
        "restock.done": "تم استيراد {n} بطاقة جديدة (تجاهل المكرر).\n\n{summary}",
        "myid": (
            "معرّف مستخدم تيليجرام: `{uid}`\n"
            "ضَع هذا الرقم في `ADMIN_IDS` داخل `.env` على الخادم، ثم أعد تشغيل البوت، وبعدها يمكنك /restock."
        ),
        "out_of_stock": "فئة {face}$ غير متوفرة حالياً. حاول لاحقاً أو تواصل مع البائع.",
        "out_of_stock.admin": (
            "\n\n(مسؤول) أرسل /restock ثم الصق أسطراً بصيغة `الفئة,الرمز` (مثال: `50,code`). "
            "إذا ظهرت «لا صلاحية»، اضبط `ADMIN_IDS` في `.env` وأعد التشغيل؛ /myid يعرض معرّفك."
        ),
        "pay.need_provider": "هذا المنتج يحتاج PAYMENT_PROVIDER_TOKEN في `.env` (ليس Stars).",
        "checkout.invalid": "منتج غير صالح.",
        "checkout.no_stock": "غير متوفر في المخزون.",
        "pay.success_no_stock": "تم استلام الدفع لكن نفد المخزون. تواصل مع البائع للاسترداد أو التوريد.\nCharge: {charge}",
        "pay.invalid_product": "طلب غير صالح. تواصل مع البائع.",
        "pay.success": "تم الدفع، الطلب #{order}. رمز(أكواد) بطاقة {label} (لا تشاركها):\n\n{body}",
        "pay.success_label": "فئة {face}$",
        "help.message": (
            "🎫 **دعم متجر البطاقات**\n\n"
            "**كيفية الشراء:**\n"
            "1. اضغط /start أو زر 🛒 المتجر\n"
            "2. تصفح البطاقات المتاحة\n"
            "3. اختر طريقة الدفع وأكمل الشراء\n"
            "4. سيتم توصيل رموز البطاقات فوراً\n\n"
            "**طرق الدفع:**\n"
            "- Telegram Wallet Pay\n"
            "- Crypto (USDT/TRC20)\n"
            "- بطاقة ائتمان/خصم\n\n"
            "**الدعم售后:**\n"
            "للمشكلات تواصل مع المسؤول: @your_username\n\n"
            "**الأوامر:**\n"
            "/start - فتح المتجر\n"
            "/help - رسالة المساعدة\n"
            "/status - عرض البطاقات المُشتراة"
        ),
        "status.no_orders": "ليس لديك أي طلبات بعد. استخدم /start لتصفح المتجر!",
        "status.orders": "📋 طلباتك:\n\n{orders}",
        "product.card_10.title": "بطاقة رقمية 10$",
        "product.card_10.description": "فئة 10$. يُرسل الرمز بعد الدفع.",
        "product.card_10.invoice_line": "بطاقة 10$",
        "product.card_20.title": "بطاقة رقمية 20$",
        "product.card_20.description": "فئة 20$. يُرسل الرمز بعد الدفع.",
        "product.card_20.invoice_line": "بطاقة 20$",
        "product.card_50.title": "بطاقة رقمية 50$",
        "product.card_50.description": "فئة 50$. يُرسل الرمز بعد الدفع.",
        "product.card_50.invoice_line": "بطاقة 50$",
        "product.card_100.title": "بطاقة رقمية 100$",
        "product.card_100.description": "فئة 100$. يُرسل الرمز بعد الدفع.",
        "product.card_100.invoice_line": "بطاقة 100$",
        "product.card_1000.title": "بطاقة رقمية 1000$",
        "product.card_1000.description": "فئة 1000$. يُرسل الرمز بعد الدفع.",
        "product.card_1000.invoice_line": "بطاقة 1000$",
    },
}


def normalize_telegram_language(language_code: Optional[str]) -> str:
    if not language_code:
        return DEFAULT_LOCALE
    primary = language_code.split("-")[0].lower()
    if primary == "ar":
        return "ar"
    return DEFAULT_LOCALE


def tr(locale: str, key: str, **kwargs: Any) -> str:
    loc = locale if locale in SUPPORTED_LOCALES else DEFAULT_LOCALE
    template = STRINGS.get(loc, STRINGS[DEFAULT_LOCALE]).get(key)
    if template is None:
        template = STRINGS[DEFAULT_LOCALE].get(key, key)
    try:
        return template.format(**kwargs)
    except KeyError:
        return template


def main_menu_keyboard(locale: str) -> ReplyKeyboardMarkup:
    loc = locale if locale in SUPPORTED_LOCALES else DEFAULT_LOCALE
    return ReplyKeyboardMarkup(
        [
            [
                KeyboardButton(tr(loc, "btn.card_10")),
                KeyboardButton(tr(loc, "btn.card_20")),
                KeyboardButton(tr(loc, "btn.card_50")),
            ],
            [
                KeyboardButton(tr(loc, "btn.card_100")),
                KeyboardButton(tr(loc, "btn.card_1000")),
            ],
            [
                KeyboardButton(tr(loc, "btn.stock")),
                KeyboardButton(tr(loc, "btn.help")),
            ],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def lang_inline_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("English", callback_data="setlang:en"),
                InlineKeyboardButton("العربية", callback_data="setlang:ar"),
            ],
        ]
    )


def _build_menu_text_index() -> dict[str, tuple[str, Optional[str]]]:
    """Localized button label -> ("buy", product_key) | ("stock", None) | ("help", None)."""
    idx: dict[str, tuple[str, Optional[str]]] = {}
    for loc in SUPPORTED_LOCALES:
        idx[tr(loc, "btn.stock")] = ("stock", None)
        idx[tr(loc, "btn.help")] = ("help", None)
        for pk in PRODUCTS:
            idx[tr(loc, f"btn.{pk}")] = ("buy", pk)
    return idx


MENU_TEXT_INDEX = _build_menu_text_index()


def resolve_menu_text(text: str) -> Optional[tuple[str, Optional[str]]]:
    return MENU_TEXT_INDEX.get(text.strip())


def format_stock_summary(locale: str, counts: dict[int, int], total: int) -> str:
    loc = locale if locale in SUPPORTED_LOCALES else DEFAULT_LOCALE
    lines = []
    for fv in FACE_VALUE_USD:
        lines.append(tr(loc, "stock.row", face=fv, count=counts.get(fv, 0)))
    lines.append(tr(loc, "stock.total", total=total))
    return "\n".join(lines)


def product_invoice_strings(locale: str, product_key: str) -> tuple[str, str, str]:
    """title, description, labeled_price_label"""
    loc = locale if locale in SUPPORTED_LOCALES else DEFAULT_LOCALE
    return (
        tr(loc, f"product.{product_key}.title"),
        tr(loc, f"product.{product_key}.description"),
        tr(loc, f"product.{product_key}.invoice_line"),
    )
