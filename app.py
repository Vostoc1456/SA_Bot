import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from database import SessionLocal, User, QuestionLog
from content import SESSION_CONTENT

load_dotenv()
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("❌ BOT_TOKEN در فایل .env تنظیم نشده!")
    exit(1)

# =============== توابع کمکی ===============
def get_user(telegram_id, username, first_name, last_name):
    db = SessionLocal()
    user = db.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            current_session="SA01_WELCOME"
        )
        db.add(user)
        db.commit()
    db.close()
    return user

def update_user_progress(telegram_id, new_node, xp_gained=0):
    db = SessionLocal()
    user = db.query(User).filter_by(telegram_id=telegram_id).first()
    if user:
        user.current_session = new_node
        user.total_xp += xp_gained
        db.commit()
    db.close()

def get_session_code_from_node(node_id):
    return node_id[:4] if node_id and len(node_id) >= 4 else None

# =============== ارسال پیام ===============
async def send_node(update: Update, context: ContextTypes.DEFAULT_TYPE, node_id: str):
    user = update.effective_user
    db_user = get_user(user.id, user.username, user.first_name, user.last_name)
    
    session_code = get_session_code_from_node(node_id)
    if not session_code:
        await update.callback_query.edit_message_text("❌ شناسه‌ی جلسه نامعتبر است.")
        return
    
    content = SESSION_CONTENT.get(session_code, {}).get("nodes", {}).get(node_id)
    if not content:
        await update.callback_query.edit_message_text("❌ محتوا یافت نشد.")
        return
    
    text = content.get("text", "")
    buttons = content.get("buttons", [])
    
    keyboard = []
    for btn in buttons:
        keyboard.append([InlineKeyboardButton(btn["text"], callback_data=btn["callback"])])
    
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    update_user_progress(user.id, node_id)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="HTML")
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="HTML")

# =============== شروع ===============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_user(user.id, user.username, user.first_name, user.last_name)
    
    text = """
🧠 <b>دوره‌ی آگاهی موقعیتی</b>

به بات آموزشی Situational Awareness خوش آمدی.

در این دوره ۱۲ جلسه‌ی آموزشی را پشت سر می‌گذاری:
👁️ مشاهده • 🧭 اسکن محیط • 🧠 آمادگی ذهنی • 🔎 تشخیص ناهنجاری • 📊 تشخیص تهدید • 📏 مدیریت فاصله • 🚪 موقعیت‌یابی • 🗣️ کاهش تنش • 🧠 OODA Loop • 🎯 سناریوهای ترکیبی • 🏆 آزمون نهایی

برای شروع، دکمه‌ی زیر را بزن.
"""
    keyboard = [[InlineKeyboardButton("▶️ شروع دوره", callback_data="SA01_WELCOME")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="HTML")

# =============== نمایش پیشرفت ===============
async def progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db_user = get_user(user.id, user.username, user.first_name, user.last_name)
    
    completed = len(db_user.completed_sessions) if db_user.completed_sessions else 0
    text = f"""
📊 <b>گزارش پیشرفت</b>

👤 {db_user.first_name}
🧠 XP: {db_user.total_xp}
📚 جلسات تکمیل‌شده: {completed}/12

✅ پاسخ‌های درست: {db_user.correct_answers}
❌ پاسخ‌های نادرست: {db_user.wrong_answers}
"""
    keyboard = [[InlineKeyboardButton("🔄 ادامه دوره", callback_data=db_user.current_session)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="HTML")

# =============== پردازش دکمه‌ها ===============
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "PROFILE":
        await progress(update, context)
        return
    elif data == "GUIDE":
        await query.edit_message_text("📚 راهنمای دوره: ...")
        return
    elif data.startswith("SA"):
        await send_node(update, context, data)
    else:
        await query.edit_message_text("❌ دکمه نامعتبر.")

# =============== اصلی ===============
def main():
    # پروکسی SOCKS5 (از mtproto2socks روی پورت 1080)
    app = (ApplicationBuilder()
           .token(BOT_TOKEN)
           .proxy("socks5://127.0.0.1:1080")
           .get_updates_proxy("socks5://127.0.0.1:1080")
           .build())
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("progress", progress))
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    print("🤖 بات راه‌اندازی شد... منتظر پیام‌ها هستم.")
    app.run_polling()

if __name__ == "__main__":
    main()