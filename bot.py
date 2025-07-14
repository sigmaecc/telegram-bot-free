
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ConversationHandler,
)
import csv
import os
import asyncio

# Define stages
NAME, PHONE = range(2)

# Admin Telegram ID
ADMIN_ID = 101998041

# CSV file to store data
DATA_FILE = "sigmaecc_users.csv"

# Initialize CSV file if not exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Phone", "Telegram Username"])

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("سلام! خوش اومدی به بات رسمی سیگما 🌟\nلطفاً اسمت رو وارد کن:")
    return NAME

# Get name
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["name"] = update.message.text
    contact_button = KeyboardButton("📱 ارسال شماره تماس", request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[contact_button]], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("حالا لطفاً شماره موبایلت رو با استفاده از دکمه زیر ارسال کن:", reply_markup=reply_markup)
    return PHONE

# Get phone number
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    phone_number = update.message.contact.phone_number if update.message.contact else update.message.text
    if not phone_number.startswith("09") or len(phone_number) != 11:
        await update.message.reply_text("شماره موبایل معتبر نیست. لطفاً شماره‌ای با ۰۹ شروع و ۱۱ رقمی وارد کن.")
        return PHONE

    name = context.user_data["name"]
    username = update.message.from_user.username or "بدون نام کاربری"

    with open(DATA_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([name, phone_number, username])

    await update.message.reply_text("ثبت نامت با موفقیت انجام شد ✅\nبه زودی باهات تماس می‌گیریم.")

    # Notify admin
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"👤 ثبت‌نام جدید:\n📝 نام: {name}\n📱 شماره: {phone_number}\n📎 یوزرنیم: @{username}"
    )

    return ConversationHandler.END

# Admin command to get number of users
async def get_users_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_ID:
        return
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        count = sum(1 for row in file) - 1
    await update.message.reply_text(f"👥 تعداد کاربران ثبت‌شده: {count}")

# Admin command to export CSV file
async def export_csv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_document(document=open(DATA_FILE, "rb"))

# Cancel handler
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("عملیات لغو شد. هر وقت خواستی /start رو بزن.")
    return ConversationHandler.END

# Build the app
def build_app(token: str):
    app = ApplicationBuilder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.CONTACT | filters.TEXT, get_phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("users", get_users_count))
    app.add_handler(CommandHandler("export", export_csv))

    return app

# Run the bot
if __name__ == "__main__":
    TOKEN = "7364645860:AAGJTAIltLb6dwf9o6qr6heSYNu8y9BV8lM"
    app = build_app(TOKEN)
    asyncio.run(app.run_polling())
