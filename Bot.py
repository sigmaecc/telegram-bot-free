
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

TOKEN = "YOUR_BOT_TOKEN"  # توکن واقعی رباتت رو اینجا وارد کن

logging.basicConfig(level=logging.INFO)

(ASK_NAME, ASK_PHONE, ASK_GRADE, ASK_FIELD, ASK_CITY) = range(5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لطفاً نام دانش‌آموز را وارد کنید:")
    return ASK_NAME

async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("شماره موبایل را وارد کنید:")
    return ASK_PHONE

async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    reply_keyboard = [["دهم", "یازدهم", "دوازدهم"]]
    await update.message.reply_text(
        "مقطع تحصیلی را انتخاب کنید:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return ASK_GRADE

async def ask_grade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["grade"] = update.message.text
    reply_keyboard = [["ریاضی", "تجربی", "انسانی", "هنر", "زبان"]]
    await update.message.reply_text(
        "رشته تحصیلی را انتخاب کنید:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return ASK_FIELD

async def ask_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["field"] = update.message.text
    await update.message.reply_text("شهر خود را وارد کنید:")
    return ASK_CITY

async def ask_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["city"] = update.message.text

    summary = f"""✅ ثبت اطلاعات:
👤 نام: {context.user_data['name']}
📞 شماره موبایل: {context.user_data['phone']}
🎓 مقطع: {context.user_data['grade']}
📚 رشته: {context.user_data['field']}
🏙 شهر: {context.user_data['city']}"""
    await update.message.reply_text(summary)

    # ارسال فایل PDF
    try:
        with open("1_17511833796.pdf", "rb") as file:
            await update.message.reply_document(file, caption="📄 فایل هدیه شما آماده است.")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا در ارسال فایل: {e}")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("فرایند لغو شد.")
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
    fallbacks=[CommandHandler("cancel", cancel)],
)

app.add_handler(conv_handler)
app.run_polling()
