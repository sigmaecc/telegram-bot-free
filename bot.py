import os
import csv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, filters, ContextTypes,
    ConversationHandler
)

ASK_NAME, ASK_PHONE = range(2)
CSV_FILE = "users.csv"
FILE_NAME = "1_17511833796.pdf"

# بررسی اینکه آیا شماره قبلاً فایل گرفته
def has_downloaded(phone):
    if not os.path.exists(CSV_FILE):
        return False
    with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return any(row['phone'] == phone for row in reader)

# ذخیره اطلاعات کاربر
def save_user(name, phone):
    file_exists = os.path.exists(CSV_FILE)
    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['name', 'phone']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({'name': name, 'phone': phone})

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لطفاً نام و نام خانوادگی خود را وارد کنید:")
    return ASK_NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text.strip()
    await update.message.reply_text("حالا لطفاً شماره موبایل خود را وارد کنید:")
    return ASK_PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    name = context.user_data["name"]

    if has_downloaded(phone):
        await update.message.reply_text("⚠️ شما قبلاً فایل را دریافت کرده‌اید.")
    else:
        await update.message.reply_text(f"{name} عزیز، فایل شما در حال ارسال است...")
        await update.message.reply_document(document=open(FILE_NAME, "rb"))
        save_user(name, phone)

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("فرایند لغو شد.")
    return ConversationHandler.END

if __name__ == "__main__":
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()
