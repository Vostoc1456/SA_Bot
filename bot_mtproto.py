from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# اطلاعات پروکسی شما
proxy = {
    "scheme": "mtproto",  # نوع پروکسی
    "hostname": "mashti.just-money.co.uk",
    "port": 8880,
    "secret": "eeNEgYdJvXrFGRMCIMJdCQ"  # کلید مخفی
}

# ساخت کلاینت با پروکسی
app = Client(
    "my_bot",
    bot_token="توکن_ربات_شما",
    proxy=proxy
)

# دستور /start
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("سلام! این ربات با پروکسی MTProto کار می‌کند.")

# اجرا
app.run()