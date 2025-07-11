import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# مراحل گفتگو
ASK_NAME, ASK_PHONE, ASK_GRADE, ASK_FIELD, ASK_CITY = range(5)

# تنظیمات لاگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# بررسی عضویت
CHANNEL_USERNAME = "@sigmaecc"
CHANNEL_LINK = "https://t.me/sigmaecc"

# مسیر فایل PDF برای ارسال
PDF_FILE_PATH = "sample.pdf"

# Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS = ServiceAccountCredentials.from_json_keyfile_name("google_credentials.json", SCOPE)
client = gspread.authorize(CREDS)
sheet = client.open("TelegramBotData").sheet1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    bot = context.bot

    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status not in ["member", "creator", "administrator"]:
            raise Exception("Not a member")
    except:
        await update.message.reply_text(f"برای دریافت فایل، لطفاً ابتدا عضو کانال شوید:
{CHANNEL_LINK}
سپس /start را بزنید.")
        return ConversationHandler.END

    await update.message.reply_text("سلام! لطفاً نام خود را وارد کنید:")
    return ASK_NAME

async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("شماره موبایل خود را وارد کنید:")
    return ASK_PHONE

async def ask_grade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("مقطع تحصیلی خود را وارد کنید:")
    return ASK_GRADE

async def ask_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["grade"] = update.message.text
    await update.message.reply_text("رشته تحصیلی خود را وارد کنید:")
    return ASK_FIELD

async def ask_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["field"] = update.message.text
    await update.message.reply_text("شهر محل سکونت خود را وارد کنید:")
    return ASK_CITY

async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["city"] = update.message.text
    data = context.user_data
    sheet.append_row([data["name"], data["phone"], data["grade"], data["field"], data["city"]])

    summary = f"""✅ ثبت اطلاعات شما با موفقیت انجام شد:
👤 نام: {data["name"]}
📱 موبایل: {data["phone"]}
🎓 مقطع: {data["grade"]}
📚 رشته: {data["field"]}
🏙️ شهر: {data["city"]}
"""

    await update.message.reply_text(summary)
    with open(PDF_FILE_PATH, "rb") as pdf:
        await update.message.reply_document(pdf)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("فرایند لغو شد.")
    return ConversationHandler.END

if __name__ == "__main__":
    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_grade)],
            ASK_GRADE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_field)],
            ASK_FIELD: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_city)],
            ASK_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, finish)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()
