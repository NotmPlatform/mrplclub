import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = int(os.environ.get("ADMIN_ID", "7964857997"))

WELCOME_TEXT = """
MRPL Club — знакомства в Мариуполе ❤️

Мы проводим вечера знакомств, где за один вечер можно познакомиться с 10–15 новыми людьми.

Форматы встреч:
• быстрые свидания
• свидания вслепую
• знакомства через игры и общение

Чтобы принять участие — отправьте заявку:

Имя:
Возраст:
Город:
Телефон:
С кем хотите познакомиться (возраст):
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message

    username = f"@{user.username}" if user.username else "без username"

    text = f"""
📩 Новая заявка

Имя: {user.first_name}
Username: {username}
ID: {user.id}

Сообщение:
{message.text}
"""

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=text
    )

    await update.message.reply_text(
        "Спасибо! Ваша заявка отправлена менеджеру."
    )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot started...")
    app.run_polling()

if name == "__main__":
    main()
