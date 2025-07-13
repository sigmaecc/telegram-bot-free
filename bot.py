
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler,
    filters, ConversationHandler
)
from gspread import service_account
import logging

logging.basicConfig(level=logging.INFO)

# متغیرها
TOKEN = os.getenv("7364645860:AAGJTAIltLb6dwf9o6qr6heSYNu8y9BV8lM")
CHANNEL_USERNAME = "@sigmaecc"
PDF_FILE_PATH = "free_file.pdf"

# مرحله‌ها
ASK_NAME, ASK_PHONE, ASK_GRADE, ASK_FIELD, ASK_CITY = range(5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    bot = context.bot

    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status not in ["member", "creator", "administrator"]:
            raise Exception("Not a member")
    except:
        await update.message.reply_text(
            f"""برای دریافت فایل، لطفاً ابتدا عضو کانال شوید:
https://t.me/sigmaecc
سپس /start را دوباره بزنید."""
        )
        return ConversationHandler.END

    await update.message.reply_text("👤 لطفاً نام خود را وارد کنید:")
    return ASK_NAME

async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("📱 لطفاً شماره موبایل خود را وارد کنید:")
    return ASK_PHONE

async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("🎓 لطفاً مقطع تحصیلی خود را وارد کنید:")
    return ASK_GRADE

async def ask_grade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["grade"] = update.message.text
    await update.message.reply_text("📚 لطفاً رشته تحصیلی خود را وارد کنید:")
    return ASK_FIELD

async def ask_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["field"] = update.message.text
    await update.message.reply_text("🌆 لطفاً شهر خود را وارد کنید:")
    return ASK_CITY

async def ask_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["city"] = update.message.text

    summary = (
        f"✅ ثبت اطلاعات:
"
        f"👤 نام: {context.user_data['name']}
"
        f"📱 شماره موبایل: {context.user_data['phone']}
"
        f"🎓 مقطع: {context.user_data['grade']}
"
        f"📚 رشته: {context.user_data['field']}
"
        f"🌆 شهر: {context.user_data['city']}"
    )

    await update.message.reply_text(summary)

    # ارسال فایل PDF
    with open(PDF_FILE_PATH, "rb") as pdf_file:
        await update.message.reply_document(pdf_file)

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⛔️ فرایند لغو شد.")
    return ConversationHandler.END

app = ApplicationBuilder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
        ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
        ASK_GRADE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_grade)],
        ASK_FIELD: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_field)],
        ASK_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_city)],
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)

app.add_handler(conv_handler)
