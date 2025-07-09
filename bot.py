import os
import csv
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, filters, ContextTypes,
    ConversationHandler
)

ASK_NAME, ASK_PHONE, ASK_GRADE, ASK_MAJOR, ASK_CITY = range(5)
CSV_FILE = "users.csv"
FILE_NAME = "1_17511833796.pdf"
CHANNEL_USERNAME = "@sigmaecc"

GRADES = ["دهم", "یازدهم", "دوازدهم"]
MAJORS = ["ریاضی", "تجربی", "انسانی"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لطفاً نام و نام خانوادگی خود را وارد کنید:")
    return ASK_NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text.strip()
    kb = [[KeyboardButton("📱 ارسال شماره من", request_contact=True)]]
    await update.message.reply_text("لطفاً شماره موبایل خود را با دکمه زیر ارسال کنید:",
                                    reply_markup=ReplyKeyboardMarkup(kb, one_time_keyboard=True, resize_keyboard=True))
    return ASK_PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    if not contact:
        await update.message.reply_text("لطفاً شماره را با استفاده از دکمه ارسال کنید.")
        return ASK_PHONE
    context.user_data["phone"] = contact.phone_number
    grade_buttons = [[grade] for grade in GRADES]
    await update.message.reply_text("مقطع تحصیلی خود را انتخاب کنید:",
                                    reply_markup=ReplyKeyboardMarkup(grade_buttons, one_time_keyboard=True, resize_keyboard=True))
    return ASK_GRADE

async def get_grade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["grade"] = update.message.text.strip()
    major_buttons = [[major] for major in MAJORS]
    await update.message.reply_text("رشته تحصیلی خود را انتخاب کنید:",
                                    reply_markup=ReplyKeyboardMarkup(major_buttons, one_time_keyboard=True, resize_keyboard=True))
    return ASK_MAJOR

async def get_major(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["major"] = update.message.text.strip()
    await update.message.reply_text("لطفاً نام شهر خود را وارد کنید:", reply_markup=None)
    return ASK_CITY

async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["city"] = update.message.text.strip()
    user_id = update.effective_user.id
    bot = context.bot
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status not in ["member", "creator", "administrator"]:
            raise Exception("Not a member")
    except:
        await channel_link = "https://t.me/sigmaecc"
await update.message.reply_text(f"برای دریافت فایل، لطفاً ابتدا عضو کانال شوید:\n{channel_link}")
{CHANNEL_USERNAME}
سپس دوباره /start را بزنید.")
        return ConversationHandler.END

    phone = context.user_data["phone"]
    if has_downloaded(phone):
        await update.message.reply_text("⚠️ شما قبلاً فایل را دریافت کرده‌اید.")
    else:
        await update.message.reply_text("✅ اطلاعات ثبت شد. فایل برای شما ارسال می‌شود...")
        await update.message.reply_document(document=open(FILE_NAME, "rb"))
        save_user(context.user_data)
    return ConversationHandler.END

def has_downloaded(phone):
    if not os.path.exists(CSV_FILE):
        return False
    with open(CSV_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return any(row['phone'] == phone for row in reader)

def save_user(data):
    file_exists = os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a", newline='', encoding='utf-8') as f:
        fieldnames = ['name', 'phone', 'grade', 'major', 'city']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            'name': data['name'],
            'phone': data['phone'],
            'grade': data['grade'],
            'major': data['major'],
            'city': data['city']
        })

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("فرایند لغو شد.")
    return ConversationHandler.END

if __name__ == "__main__":
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            ASK_PHONE: [MessageHandler(filters.CONTACT, get_phone)],
            ASK_GRADE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_grade)],
            ASK_MAJOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_major)],
            ASK_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv)
    app.run_polling()


# اجرای Flask برای فریب Render که منتظر پورت هست
from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running."

def run_flask():
    app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run_flask).start()
