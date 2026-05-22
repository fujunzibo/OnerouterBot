import asyncio
import logging
import re
from typing import Optional

from aiohttp import web

from telegram import LabeledPrice, Update, WebAppInfo, MenuButtonWebApp
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PreCheckoutQueryHandler,
    filters,
)

from config import (
    ADMIN_IDS,
    BOT_TOKEN,
    PAYMENT_PROVIDER_TOKEN,
    PRODUCTS,
    TELEGRAM_PROXY,
    TELEGRAM_TRUST_ENV,
    WEBHOOK_HOST,
    WEBHOOK_PORT,
    WEBHOOK_PATH,
    WEBHOOK_SECRET,
    WEBAPP_HOST,
    create_telegram_http_request,
)
from db import (
    add_tokens,
    count_available_for_face,
    count_available_tokens,
    ensure_locale_row,
    face_value_from_payload,
    fulfill_order,
    get_locale,
    init_db,
    set_locale,
    stock_counts_by_face,
)
from i18n import (
    SUPPORTED_LOCALES,
    format_stock_summary,
    lang_inline_keyboard,
    main_menu_keyboard,
    product_invoice_strings,
    resolve_menu_text,
    tr,
)

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def _is_admin(user_id: Optional[int]) -> bool:
    if user_id is None or not ADMIN_IDS:
        return False
    return user_id in ADMIN_IDS


def _locale(update: Update) -> str:
    u = update.effective_user
    if not u:
        return "en"
    return ensure_locale_row(u.id, u.language_code)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat or not update.effective_user:
        return
    loc = _locale(update)
    stock_counts = stock_counts_by_face()
    stock_total = sum(stock_counts.values())
    stock_summary = format_stock_summary(loc, stock_counts, stock_total)
    
    # 创建 WebApp 按钮
    webapp_info = WebAppInfo(url=f"{WEBAPP_HOST.rstrip('/')}/webapp")
    
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Open Store", web_app=webapp_info)],
    ])
    
    welcome_text = f"{tr(loc, 'start.welcome')}\n\n{stock_summary}"
    await update.effective_chat.send_message(
        welcome_text,
        reply_markup=keyboard,
        parse_mode="Markdown",
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat or not update.effective_user:
        return
    loc = _locale(update)
    help_text = tr(loc, "help.message")
    await update.effective_chat.send_message(help_text, parse_mode="Markdown")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat or not update.effective_user:
        return
    loc = _locale(update)
    user_id = update.effective_user.id
    
    from db import get_user_orders
    orders = get_user_orders(user_id)
    
    if not orders:
        await update.effective_chat.send_message(tr(loc, "status.no_orders"))
        return
    
    orders_text = "\n\n".join([
        f"📦 Order #{order['id']}\n"
        f"   Amount: ${order['total']}\n"
        f"   Status: {order['status']}\n"
        f"   Date: {order['created_at']}"
        for order in orders
    ])
    
    await update.effective_chat.send_message(
        tr(loc, "status.orders", orders=orders_text),
        parse_mode="Markdown",
    )


async def cmd_lang(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_user:
        return
    loc = _locale(update)
    await update.message.reply_text(
        tr(loc, "lang.choose"),
        reply_markup=lang_inline_keyboard(),
    )


async def on_setlang(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    if not q or not q.data or not q.from_user:
        return
    await q.answer()
    parts = q.data.split(":")
    if len(parts) != 2 or parts[0] != "setlang":
        return
    lang = parts[1]
    if lang not in SUPPORTED_LOCALES:
        return
    set_locale(q.from_user.id, lang)
    try:
        await q.edit_message_text(tr(lang, "lang.confirm"))
    except Exception:
        logger.debug("Could not edit language prompt message", exc_info=True)
    await context.bot.send_message(
        chat_id=q.from_user.id,
        text=tr(lang, "start.welcome"),
        reply_markup=main_menu_keyboard(lang),
    )


async def cmd_restock(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user or not update.message:
        return
    if not _is_admin(update.effective_user.id):
        loc = _locale(update)
        await update.message.reply_text(tr(loc, "err.no_permission"))
        return
    context.user_data["awaiting_restock"] = True
    loc = _locale(update)
    await update.message.reply_text(tr(loc, "restock.prompt"))


async def cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop("awaiting_restock", None)
    loc = _locale(update)
    await update.message.reply_text(
        tr(loc, "cancel.done"),
        reply_markup=main_menu_keyboard(loc),
    )


async def cmd_myid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user or not update.message:
        return
    u = update.effective_user
    loc = _locale(update)
    await update.message.reply_text(
        tr(loc, "myid", uid=u.id),
        parse_mode="Markdown",
    )


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_user:
        return
    loc = _locale(update)

    if context.user_data.get("awaiting_restock") and _is_admin(update.effective_user.id):
        text = update.message.text or ""
        n = add_tokens(text.splitlines())
        context.user_data.pop("awaiting_restock", None)
        counts = stock_counts_by_face()
        total = count_available_tokens()
        summary = format_stock_summary(loc, counts, total)
        await update.message.reply_text(
            tr(loc, "restock.done", n=n, summary=summary),
            reply_markup=main_menu_keyboard(loc),
        )
        return

    text = (update.message.text or "").strip()
    action = resolve_menu_text(text)
    if not action:
        await update.message.reply_text(
            tr(loc, "fallback.buttons"),
            reply_markup=main_menu_keyboard(loc),
        )
        return

    kind, payload = action[0], action[1]
    if kind == "buy" and payload:
        await send_invoice(update, context, payload, loc)
    elif kind == "stock":
        counts = stock_counts_by_face()
        total = count_available_tokens()
        await update.message.reply_text(
            format_stock_summary(loc, counts, total),
            reply_markup=main_menu_keyboard(loc),
        )
    elif kind == "help":
        await update.message.reply_text(
            tr(loc, "help.body"),
            reply_markup=main_menu_keyboard(loc),
        )


async def send_invoice(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    product_key: str,
    loc: str,
) -> None:
    if not update.effective_chat or not update.message:
        return
    p = PRODUCTS[product_key]
    face = p["face_value_usd"]
    if count_available_for_face(face) < 1:
        msg = tr(loc, "out_of_stock", face=face)
        if update.effective_user and _is_admin(update.effective_user.id):
            msg += tr(loc, "out_of_stock.admin")
        await update.message.reply_text(
            msg,
            reply_markup=main_menu_keyboard(loc),
        )
        return

    currency = p["currency"]
    if currency != "XTR" and not PAYMENT_PROVIDER_TOKEN:
        await update.message.reply_text(
            tr(loc, "pay.need_provider"),
            reply_markup=main_menu_keyboard(loc),
        )
        return

    provider_token = PAYMENT_PROVIDER_TOKEN if currency != "XTR" else (PAYMENT_PROVIDER_TOKEN or "")

    title, description, line_label = product_invoice_strings(loc, product_key)
    prices = [LabeledPrice(line_label, p["price_stars"])]
    await context.bot.send_invoice(
        chat_id=update.effective_chat.id,
        title=title,
        description=description,
        payload=p["payload"],
        provider_token=provider_token,
        currency=currency,
        prices=prices,
    )


def _locale_from_user_id(user_id: int, language_code: Optional[str]) -> str:
    stored = get_locale(user_id)
    if stored and stored in SUPPORTED_LOCALES:
        return stored
    return ensure_locale_row(user_id, language_code)


async def pre_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.pre_checkout_query
    if not q or not q.from_user:
        return
    loc = _locale_from_user_id(q.from_user.id, q.from_user.language_code)
    payload = q.invoice_payload
    if payload not in PRODUCTS:
        err = tr(loc, "checkout.invalid")[:200]
        await q.answer(ok=False, error_message=err)
        return
    face = face_value_from_payload(payload)
    if face is None or count_available_for_face(face) < 1:
        err = tr(loc, "checkout.no_stock")[:200]
        await q.answer(ok=False, error_message=err)
        return
    await q.answer(ok=True)


async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.message
    if not msg or not msg.successful_payment or not update.effective_user:
        return
    sp = msg.successful_payment
    username = update.effective_user.username
    user_id = update.effective_user.id
    loc = _locale_from_user_id(user_id, update.effective_user.language_code)

    try:
        order_id, tokens = fulfill_order(
            user_id=user_id,
            product_payload=sp.invoice_payload,
            telegram_payment_charge_id=sp.telegram_payment_charge_id,
            provider_payment_charge_id=sp.provider_payment_charge_id,
            amount=sp.total_amount,
            currency=sp.currency,
            username=username,
        )
    except RuntimeError as e:
        if str(e) == "insufficient_stock":
            await msg.reply_text(
                tr(
                    loc,
                    "pay.success_no_stock",
                    charge=sp.telegram_payment_charge_id or "",
                )
            )
            logger.error("Stock race for user %s charge %s", user_id, sp.telegram_payment_charge_id)
            return
        if str(e) == "invalid_product":
            await msg.reply_text(tr(loc, "pay.invalid_product"))
            return
        raise

    body = "\n".join(tokens)
    fv = face_value_from_payload(sp.invoice_payload)
    label = tr(loc, "pay.success_label", face=fv) if fv is not None else ""
    await msg.reply_text(
        tr(loc, "pay.success", order=order_id, label=label, body=body),
        reply_markup=main_menu_keyboard(loc),
    )


def main() -> None:
    if not BOT_TOKEN:
        raise SystemExit("请设置环境变量 BOT_TOKEN")

    if not WEBHOOK_HOST:
        raise SystemExit("请设置环境变量 WEBHOOK_HOST（例如 https://yourdomain.com）")

    init_db()

    webhook_url = f"{WEBHOOK_HOST.rstrip('/')}{WEBHOOK_PATH}"

    http_request = create_telegram_http_request()
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .request(http_request)
        .get_updates_request(http_request)
        .build()
    )
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("lang", cmd_lang))
    app.add_handler(CommandHandler("language", cmd_lang))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("myid", cmd_myid))
    app.add_handler(CommandHandler("restock", cmd_restock))
    app.add_handler(CommandHandler("cancel", cmd_cancel))
    app.add_handler(CallbackQueryHandler(on_setlang, pattern=re.compile(r"^setlang:(en|ar)$")))
    app.add_handler(PreCheckoutQueryHandler(pre_checkout))
    app.add_handler(
        MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment)
    )
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))

    async def process_update(update: Update) -> None:
        await app.process_update(update)

    async def webhook_handler(request: web.Request) -> web.Response:
        if request.method != "POST":
            return web.Response(status=405)
        if request.path != WEBHOOK_PATH:
            return web.Response(status=404)
        secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if secret != WEBHOOK_SECRET:
            return web.Response(status=403)
        try:
            data = await request.json()
        except Exception:
            return web.Response(status=400)
        update = Update.de_json(data, app.bot)
        asyncio.create_task(process_update(update))
        return web.Response(status=200)

    async def on_startup(_app: web.Application) -> None:
        await app.initialize()
        await app.bot.set_webhook(webhook_url, secret_token=WEBHOOK_SECRET)
        logger.info(f"Webhook set to {webhook_url}")
        
        # 设置菜单按钮（使用 WebApp）
        try:
            webapp_info = WebAppInfo(url=f"{WEBAPP_HOST.rstrip('/')}/webapp")
            menu_button = MenuButtonWebApp(text="🛒 Store", web_app=webapp_info)
            await app.bot.set_chat_menu_button(menu_button=menu_button)
            logger.info("Menu button set")
        except Exception as e:
            logger.warning(f"Could not set menu button: {e}")
        
        # 设置命令列表
        await app.bot.set_my_commands([
            ("start", "Welcome & Open Store"),
            ("help", "Support & After-sales"),
            ("status", "View purchased cards"),
        ])
        logger.info("Bot commands set")

    async def on_shutdown(_app: web.Application) -> None:
        await app.stop()
        await app.bot.delete_webhook()
        logger.info("Webhook deleted")

    # WebApp API 路由
    async def api_stock(request: web.Request) -> web.Response:
        stock = stock_counts_by_face()
        return web.json_response(stock)
    
    async def api_create_order(request: web.Request) -> web.Response:
        try:
            data = await request.json()
            items = data.get('items', [])
            total = data.get('total', 0)
            payment_method = data.get('paymentMethod', 'card')
            
            if not items or total <= 0:
                return web.json_response({'error': 'Invalid order data'}, status=400)
            
            # 处理订单逻辑
            from db import create_order, get_tokens_for_order
            order_id = create_order(total, payment_method, data.get('telegramData'))
            
            # 分配卡片
            tokens = []
            for item in items:
                face_value = item.get('faceValue', item.get('price', 10))
                quantity = item.get('quantity', 1)
                tokens.extend(get_tokens_for_order(face_value, quantity))
            
            return web.json_response({
                'orderId': order_id,
                'total': total,
                'paymentMethod': payment_method,
                'tokens': tokens
            })
        except Exception as e:
            logger.error("API create_order error", exc_info=True)
            return web.json_response({'error': str(e)}, status=500)
    
    # 静态文件服务
    from pathlib import Path
    webapp_dir = Path(__file__).resolve().parent / 'webapp' / 'dist'
    
    async def serve_webapp(request: web.Request) -> web.Response:
        path = request.match_info.get('path', 'index.html')
        file_path = webapp_dir / path
        
        if not file_path.exists():
            file_path = webapp_dir / 'index.html'
        
        if not file_path.exists():
            return web.Response(status=404)
        
        content_type = 'text/html'
        if path.endswith('.js'):
            content_type = 'application/javascript'
        elif path.endswith('.css'):
            content_type = 'text/css'
        elif path.endswith('.png'):
            content_type = 'image/png'
        elif path.endswith('.jpg') or path.endswith('.jpeg'):
            content_type = 'image/jpeg'
        
        with open(file_path, 'rb') as f:
            content = f.read()
        
        return web.Response(body=content, content_type=content_type)
    
    server = web.Application()
    server.on_startup.append(on_startup)
    server.on_shutdown.append(on_shutdown)
    server.router.add_post(WEBHOOK_PATH, webhook_handler)
    server.router.add_get('/api/stock', api_stock)
    server.router.add_post('/api/create-order', api_create_order)
    server.router.add_get('/webapp/{path:.*}', serve_webapp)
    server.router.add_get('/webapp', serve_webapp)

    logger.info(
        "Bot starting in webhook mode… (TELEGRAM_TRUST_ENV=%s, TELEGRAM_PROXY=%s)",
        TELEGRAM_TRUST_ENV,
        TELEGRAM_PROXY or "none",
    )
    web.run_app(server, host="0.0.0.0", port=WEBHOOK_PORT, print=None)


if __name__ == "__main__":
    main()
