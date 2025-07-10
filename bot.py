
import logging
from telegram import Update, InputFile
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler,
    filters, ContextTypes
)
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- تنظیمات ---
TOKEN = "YOUR_BOT_TOKEN"
CHANNEL_USERNAME = "@sigmaecc"
PDF_FILE_PATH = "1_17511833796.pdf"
CREDENTIALS_FILE = "credentials.json"

ASK_NAME, ASK_PHONE, ASK_GRADE, ASK_MAJOR, ASK_CITY = range(5)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

def save_to_sheets(name, phone, city, grade, field):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)

    sheet = client.open("Bot Feedback").sheet1
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    sheet.append_row([name, phone, city, grade, field, now])

async def check_membership(user_id, bot):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "creator", "administrator"]
    except Exception:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لطفاً نام و نام خانوادگی خود را وارد کنید:")
    return ASK_NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    if len(name) < 3:
        await update.message.reply_text("❌ لطفاً نام معتبری وارد کنید.")
        return ASK_NAME

    context.user_data["name"] = name
    await update.message.reply_text("شماره موبایل خود را وارد کنید:")
    return ASK_PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    if not phone.startswith("09") or len(phone) != 11 or not phone.isdigit():
        await update.message.reply_text("❌ شماره موبایل نامعتبر است. لطفاً شماره‌ای با فرمت صحیح وارد کنید.")
        return ASK_PHONE

    context.user_data["phone"] = phone
    await update.message.reply_text("مقطع تحصیلی خود را وارد کنید (مثلاً دهم، یازدهم، کنکور):")
    return ASK_GRADE

async def get_grade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    grade = update.message.text.strip()
    valid_grades = ["دهم", "یازدهم", "دوازدهم", "کنکور", "فارغ‌التحصیل"]
    if grade not in valid_grades:
        await update.message.reply_text("❌ لطفاً یکی از مقاطع زیر را وارد کنید:
" + ", ".join(valid_grades))
        return ASK_GRADE

    context.user_data["grade"] = grade
    await update.message.reply_text("رشته تحصیلی خود را وارد کنید (مثلاً ریاضی، تجربی):")
    return ASK_MAJOR

async def get_major(update: Update, context: ContextTypes.DEFAULT_TYPE):
    major = update.message.text.strip()
    valid_majors = ["ریاضی", "تجربی", "انسانی", "هنر", "زبان"]
    if major not in valid_majors:
        await update.message.reply_text("❌ لطفاً یکی از رشته‌های زیر را وارد کنید:
" + ", ".join(valid_majors))
        return ASK_MAJOR

    context.user_data["major"] = major
    await update.message.reply_text("شهر محل تحصیل خود را وارد کنید:")
    return ASK_CITY

async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["city"] = update.message.text.strip()
    user_id = update.effective_user.id
    bot = context.bot

    is_member = await check_membership(user_id, bot)
    if not is_member:
        await update.message.reply_text("برای دریافت فایل، ابتدا عضو کانال شوید:\nhttps://t.me/sigmaecc\nو سپس /start را بزنید.")
        return ConversationHandler.END

    name = context.user_data["name"]
    phone = context.user_data["phone"]
    city = context.user_data["city"]
    grade = context.user_data["grade"]
    major = context.user_data["major"]

    save_to_sheets(name, phone, city, grade, major)

    with open(PDF_FILE_PATH, "rb") as f:
        await update.message.reply_document(InputFile(f), caption="📄 فایل شما آماده است.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("عملیات لغو شد.")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            ASK_GRADE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_grade)],
            ASK_MAJOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_major)],
            ASK_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
