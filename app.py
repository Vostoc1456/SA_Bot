import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

load_dotenv()
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("❌ BOT_TOKEN تنظیم نشده!")
    exit(1)

# =============== محتوای دوره ===============
CONTENT = {
    "start": """
🧠 <b>دوره‌ی آگاهی موقعیتی</b>

به بات آموزشی خوش آمدی.

این دوره شامل ۱۲ جلسه است:
• Situational Awareness
• Observation
• Mental Readiness
• Environmental Scanning
• Baseline & Anomaly
• Threat Recognition
• Proxemics
• Positioning & Exit Routes
• De-escalation
• OODA Loop
• Integrated Scenarios
• Final Assessment

برای شروع، دکمه‌ی زیر را بزن.
""",
    "lesson1": """
🛡️ <b>جلسه ۱ — آگاهی موقعیتی</b>

<i>Situational Awareness</i>

اولین مهارتی که باید یاد بگیری، توانایی «دیدن» نیست؛ بلکه توانایی درک محیط است.

در این جلسه یاد می‌گیری:
• Situational Awareness چیست؟
• چرا دیدن با مشاهده کردن فرق دارد؟
• چرا هر رفتار غیرعادی الزاماً تهدید نیست؟

<b>آماده‌ای؟</b>
""",
    "quiz1": """
🧪 <b>تمرین</b>

کدام گزینه یک <b>Observation</b> است؟

A) این فرد خطرناک است.
B) این فرد چند بار به سمت ورودی نگاه کرد.
C) او احتمالاً قصد حمله دارد.
D) رفتار او مشکوک است.
""",
    "feedback_correct": """
✅ درست است!

«چند بار به سمت ورودی نگاه کرد» چیزی است که مستقیماً مشاهده شده است.
گزینه‌های دیگر وارد مرحله تفسیر یا قضاوت شده‌اند.

<b>+20 XP</b>
""",
    "feedback_wrong": """
❌ پاسخ صحیح: <b>B</b>

«چند بار به سمت ورودی نگاه کرد» یک Observation خالص است.
گزینه‌های دیگر تفسیر یا قضاوت هستند.

<b>دوباره امتحان کن!</b>
"""
}

# =============== پاسخ‌های صحیح ===============
QUIZ_ANSWERS = {
    "quiz1": "B"
}

# =============== توابع ===============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("▶️ شروع دوره", callback_data="lesson1")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(CONTENT["start"], reply_markup=reply_markup, parse_mode="HTML")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "lesson1":
        keyboard = [[InlineKeyboardButton("🧪 تمرین", callback_data="quiz1")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(CONTENT["lesson1"], reply_markup=reply_markup, parse_mode="HTML")
    
    elif data == "quiz1":
        # دکمه‌های گزینه‌ها
        keyboard = [
            [InlineKeyboardButton("A", callback_data="quiz1_A")],
            [InlineKeyboardButton("B", callback_data="quiz1_B")],
            [InlineKeyboardButton("C", callback_data="quiz1_C")],
            [InlineKeyboardButton("D", callback_data="quiz1_D")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(CONTENT["quiz1"], reply_markup=reply_markup, parse_mode="HTML")
    
    elif data.startswith("quiz1_"):
        # استخراج پاسخ انتخاب‌شده
        selected = data.split("_")[1]  # A, B, C, D
        correct = QUIZ_ANSWERS["quiz1"]
        
        if selected == correct:
            feedback = CONTENT["feedback_correct"]
        else:
            feedback = CONTENT["feedback_wrong"]
        
        keyboard = [[InlineKeyboardButton("📚 ادامه دوره", callback_data="lesson2")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(feedback, reply_markup=reply_markup, parse_mode="HTML")
    
    elif data == "lesson2":
        await query.edit_message_text("🎉 جلسه ۲ به زودی اضافه می‌شود!")

# =============== اصلی ===============
def main():
    # تنظیم تایم‌اوت برای جلوگیری از قطعی
    app = (ApplicationBuilder()
           .token(BOT_TOKEN)
           .read_timeout(60)
           .get_updates_read_timeout(60)
           .build())
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    print("🤖 بات راه‌اندازی شد... منتظر پیام‌ها هستم.")
    app.run_polling()

if __name__ == "__main__":
    main()
