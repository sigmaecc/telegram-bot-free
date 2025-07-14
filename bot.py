
from telegram import Update, InputFile
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ConversationHandler, ContextTypes
)

# Conversation states
ASK_NAME, ASK_PHONE, ASK_GRADE, ASK_FIELD, ASK_CITY = range(5)

# Replace this with your actual bot token
TOKEN = "7364645860:AAGJTAIltLb6dwf9o6qr6heSYNu8y9BV8lM"

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لطفاً نام خود را وارد کنید:")
    return ASK_NAME

# Ask for name
async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("شماره موبایل خود را وارد کنید:")
    return ASK_PHONE

# Ask for phone number
async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("مقطع تحصیلی خود را وارد کنید:")
    return ASK_GRADE

# Ask for grade
async def ask_grade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["grade"] = update.message.text
    await update.message.reply_text("رشته خود را وارد کنید:")
    return ASK_FIELD

# Ask for field
async def ask_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["field"] = update.message.text
    await update.message.reply_text("شهر خود را وارد کنید:")
    return ASK_CITY

# Ask for city and send summary + PDF
async def ask_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["city"] = update.message.text

    summary = (
    f"✅ ثبت اطلاعات:\n"
    f"🧑‍💼 نام: {context.user_data['name']}\n"
    f"📱 موبایل شماره: {context.user_data['phone']}\n"
    f"🎓 مقطع: {context.user_data['grade']}\n"
    f"📚 رشته: {context.user_data['field']}\n"
    f"🏙️ شهر: {context.user_data['city']}"
)

    await update.message.reply_text(summary)

    # Send the free PDF file
    pdf_path = "free_file.pdf"
    with open(pdf_path, "rb") as file:
        await update.message.reply_document(document=InputFile(file), filename="راهنمای رایگان.pdf")

    return ConversationHandler.END

# Cancel handler
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("فرآیند لغو شد.")
    return ConversationHandler.END

# Build the bot
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

if __name__ == "__main__":
    app.run_polling()
