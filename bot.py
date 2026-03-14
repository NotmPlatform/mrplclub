import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def parse_chat_id(value: str):
    value = value.strip()
    if value.lstrip("-").isdigit():
        return int(value)
    if value.startswith("@"):
        return value
    raise ValueError("ADMIN_ID должен быть числом или @channelusername")


WELCOME_TEXT = """
<b>MRPL Club — знакомства в Мариуполе ❤️</b>

Мы проводим вечера знакомств, где за один вечер можно познакомиться с 10–15 новыми людьми.

<b>Форматы встреч:</b>
• быстрые свидания
• свидания вслепую
• знакомства через игры и общение

<b>Чтобы принять участие — скопируйте шаблон ниже, вставьте его в сообщение и заполните:</b>

<blockquote>
Имя:
Возраст:
Город:
Телефон:
С кем хотите познакомиться (возраст):
</blockquote>

<b>Пример заполнения:</b>

Имя: Алексей
Возраст: 29
Город: Мариуполь
Телефон: +7XXXXXXXXXX
С кем хотите познакомиться (возраст): 24–32
""".strip()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(
            WELCOME_TEXT,
            parse_mode="HTML"
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(
            "Нажмите /start, скопируйте шаблон из цитаты и заполните его.",
            parse_mode="HTML"
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    admin_id_raw = os.getenv("ADMIN_ID")
    if not admin_id_raw:
        await update.message.reply_text("Ошибка: не найден ADMIN_ID")
        return

    admin_chat_id = parse_chat_id(admin_id_raw)

    user = update.effective_user
    message = update.message

    username = f"@{user.username}" if user and user.username else "без username"
    first_name = user.first_name if user and user.first_name else "-"
    user_id = user.id if user else "-"

    text = message.text if message.text else "Пустое сообщение"

    msg = (
        "📩 Новая заявка MRPL Club\n\n"
        f"Имя в Telegram: {first_name}\n"
        f"Username: {username}\n"
        f"Telegram ID: {user_id}\n\n"
        f"Сообщение:\n{text}"
    )

    try:
        await context.bot.send_message(chat_id=admin_chat_id, text=msg)
        await update.message.reply_text(
            "Спасибо! Ваша заявка принята ❤️\n\nМенеджер MRPL Club свяжется с вами."
        )
    except Exception as e:
        logger.exception("Ошибка при отправке заявки: %s", e)
        await update.message.reply_text("Не удалось отправить заявку. Попробуйте позже.")


def main():
    bot_token = os.getenv("BOT_TOKEN")
    admin_id = os.getenv("ADMIN_ID")

    if not bot_token:
        raise ValueError("Не найдена переменная окружения BOT_TOKEN")

    if not admin_id:
        raise ValueError("Не найдена переменная окружения ADMIN_ID")

    app = ApplicationBuilder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot started...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
