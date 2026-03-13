import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8689837582:AAFjWKXzdVznU5awVfThbYunwx_rYitWkwU"
ADMIN_ID = int(os.environ["ADMIN_ID"])

WELCOME_TEXT = """
MRPL Club — знакомства в Мариуполе ❤️

Мы проводим вечера знакомств, где за один вечер можно познакомиться с 10–15 новыми людьми.

Форматы встреч:
• быстрые свидания
• свидания вслепую
• знакомства через игры и общение

Чтобы принять участие — отправьте заявку по форме:

Имя:
Возраст:
Город:
Телефон:
С кем хотите познакомиться (возраст):

Пример:
Имя: Алексей
Возраст: 29
Город: Мариуполь
Телефон: +7XXXXXXXXXX
С кем хотите познакомиться (возраст): 24–32
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message

    username = f"@{user.username}" if user.username else "без username"

    header = (
        "📩 Новая заявка MRPL Club\n\n"
        f"Имя в Telegram: {user.first_name or '-'}\n"
        f"Username: {username}\n"
        f"Telegram ID: {user.id}\n\n"
        "Сообщение:\n"
    )

    if message.text:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=header + message.text
        )
    else:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=header + "Пользователь отправил сообщение неподдерживаемого типа."
        )

    await update.message.reply_text(
        "Спасибо! Ваша заявка принята ❤️\n\n"
        "Менеджер MRPL Club свяжется с вами."
    )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot started...")
    app.run_polling()

if name == "__main__":
    main()
