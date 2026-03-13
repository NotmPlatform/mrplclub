import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "7964857997"))

WELCOME_TEXT = """
MRPL Club — знакомства в Мариуполе ❤️

Мы проводим вечера знакомств, где за один вечер можно познакомиться с 10–15 новыми людьми.

Форматы встреч:
• быстрые свидания
• свидания вслепую
• знакомства через игры и общение

✨ Многие участники находят интересные знакомства уже на первом мероприятии.

Количество мест на каждый вечер ограничено, поэтому мы принимаем заявки заранее.

📩 Чтобы принять участие — отправьте заявку по форме:

Имя:
Возраст:
Город:
Телефон:
С кем хотите познакомиться (возраст):

Укажите возрастной диапазон, например: 24–32

Пример заявки:

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
    elif message.photo:
        caption = message.caption if message.caption else "Фото без подписи"
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=message.photo[-1].file_id,
            caption=header + caption
        )
    elif message.video:
        caption = message.caption if message.caption else "Видео без подписи"
        await context.bot.send_video(
            chat_id=ADMIN_ID,
            video=message.video.file_id,
            caption=header + caption
        )
    elif message.document:
        caption = message.caption if message.caption else f"Документ: {message.document.file_name}"
        await context.bot.send_document(
            chat_id=ADMIN_ID,
            document=message.document.file_id,
            caption=header + caption
        )
    else:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=header + "Пользователь отправил неподдерживаемый тип сообщения."
        )

    await update.message.reply_text(
        "Спасибо! Ваша заявка принята ❤️\n\n"
        "Менеджер MRPL Club свяжется с вами, когда откроется регистрация на ближайший вечер знакомств."
    )

def main():
    if not BOT_TOKEN:
        raise ValueError("Переменная BOT_TOKEN не задана")
    if not ADMIN_ID:
        raise ValueError("Переменная ADMIN_ID не задана")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(
            filters.TEXT | filters.PHOTO | filters.VIDEO | filters.Document.ALL,
            handle_message
        )
    )

    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
