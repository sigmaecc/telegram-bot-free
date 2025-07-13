import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)
from telegram.constants import ParseMode

# مراحل گفتگو
ASK_NAME, ASK_PHONE, ASK_GRADE, ASK_FIELD, ASK_CITY = range(5)

# توکن ربات
TOKEN = "YOUR_BOT_TOKEN"

# تابع شروع
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لطفا نام خود را وارد کنید:")
    return ASK_NAME

# دریافت نام
async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("شماره موبایل خود را وارد کنید:")
    return ASK_PHONE

# دریافت شماره موبایل
async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("مقطع تحصیلی خود را وارد کنید:")
    return ASK_GRADE

# دریافت مقطع
async def ask_grade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["grade"] = update.message.text
    await update.message.reply_text("رشته تحصیلی خود را وارد کنید:")
    return ASK_FIELD

# دریافت رشته
async def ask_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["field"] = update.message.text
    await update.message.reply_text("شهر محل سکونت خود را وارد کنید:")
    return ASK_CITY

# دریافت شهر و خلاصه اطلاعات و ارسال فایل
async def ask_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["city"] = update.message.text

    summary = (
        f"✅ ثبت اطلاعات:
"
        f"👤 نام: {context.user_data['name']}
"
        f"📞 موبایل: {context.user_data['phone']}
"
        f"📚 مقطع: {context.user_data['grade']}
"
        f"🧪 رشته: {context.user_data['field']}
"
        f"🏙 شهر: {context.user_data['city']}"
    )
    await update.message.reply_text(summary)

    # ارسال فایل pdf
    with open("free_file.pdf", "rb") as f:
        await update.message.reply_document(document=f)

    return ConversationHandler.END

# لغو عملیات
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("فرایند لغو شد.")
    return ConversationHandler.END

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

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
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()
