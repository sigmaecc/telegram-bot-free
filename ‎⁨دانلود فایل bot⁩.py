
import logging
from telegram import Update, InputFile
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler,
    filters, ContextTypes
)

# تنظیمات اولیه
TOKEN = "YOUR_BOT_TOKEN"
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
    await update.message.reply_text("سلام! لطفاً شماره موبایل خود را ارسال کنید:")
    return ASK_PHONE

# گرفتن شماره
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("مقطع تحصیلی خود را وارد کنید (مثلاً دهم، یازدهم، کنکور):")
    return ASK_GRADE

# گرفتن مقطع
async def get_grade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["grade"] = update.message.text
    await update.message.reply_text("رشته تحصیلی خود را وارد کنید (مثلاً ریاضی، تجربی):")
    return ASK_MAJOR

# گرفتن رشته
async def get_major(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["major"] = update.message.text
    await update.message.reply_text("شهر محل تحصیل خود را وارد کنید:")
    return ASK_CITY

# گرفتن شهر و بررسی عضویت و ارسال فایل
async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["city"] = update.message.text
    user_id = update.effective_user.id
    bot = context.bot

    is_member = await check_membership(user_id, bot)
    if not is_member:
        channel_link = "https://t.me/sigmaecc"
        await update.message.reply_text(
            f"برای دریافت فایل، لطفاً ابتدا عضو کانال شوید:\n{channel_link}\nسپس دستور /start را بزنید."
        )
        return ConversationHandler.END

    # ارسال فایل
    with open(PDF_FILE_PATH, "rb") as f:
        await update.message.reply_document(InputFile(f), caption="📄 فایل شما آماده است.")
    return ConversationHandler.END

# لغو
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("عملیات لغو شد.")
    return ConversationHandler.END

# اجرای برنامه
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
