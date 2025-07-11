
import logging
from telegram import Update, InputFile, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler,
    filters, ContextTypes
)

# تنظیمات اولیه
TOKEN = "7364645860:AAGJTAIltLb6dwf9o6qr6heSYNu8y9BV8lM"
CHANNEL_USERNAME = "@sigmaecc"
PDF_FILE_PATH = "1_17511833796.pdf"

# وضعیت گفتگوها
ASK_PHONE, ASK_GRADE, ASK_MAJOR, ASK_CITY = range(4)

# لاگ‌گیری
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# بررسی عضویت در کانال
async def check_membership(user_id, bot):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "creator", "administrator"]
    except Exception:
        return False

# شروع
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    is_member = await check_membership(user.id, context.bot)

    if not is_member:
        await update.message.reply_text(
            "برای دریافت فایل رایگان لطفاً ابتدا در کانال عضو شوید:
"
            "https://t.me/sigmaecc
"
            "سپس دوباره /start را بزنید."
        )
        return ConversationHandler.END

    await update.message.reply_text("سلام! لطفاً شماره موبایل خود را ارسال کنید:")
    return ASK_PHONE

# گرفتن شماره
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    reply_keyboard = [["دهم", "یازدهم", "دوازدهم"]]
    await update.message.reply_text(
        "مقطع تحصیلی را انتخاب کنید:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return ASK_GRADE

# گرفتن مقطع
async def get_grade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["grade"] = update.message.text
    reply_keyboard = [["ریاضی", "تجربی", "انسانی", "هنر", "زبان"]]
    await update.message.reply_text(
        "رشته تحصیلی را انتخاب کنید:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return ASK_MAJOR

# گرفتن رشته
async def get_major(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["major"] = update.message.text
    await update.message.reply_text("شهر محل سکونت خود را وارد کنید:")
    return ASK_CITY

# گرفتن شهر و ارسال فایل
async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["city"] = update.message.text
    user_data = context.user_data

    summary = f"""✅ ثبت اطلاعات:
📱 شماره: {user_data['phone']}
🎓 مقطع: {user_data['grade']}
📘 رشته: {user_data['major']}
🏙 شهر: {user_data['city']}"""
    await update.message.reply_text(summary)

    try:
        with open(PDF_FILE_PATH, "rb") as f:
            await update.message.reply_document(f, caption="📄 فایل رایگان شما:")
    except Exception as e:
        await update.message.reply_text("❌ خطا در ارسال فایل.")

    return ConversationHandler.END

# لغو
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("فرایند لغو شد.")
    return ConversationHandler.END

# اجرای ربات
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
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
