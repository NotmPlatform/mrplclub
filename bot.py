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

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")  # личный ID числом, например 294491997

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
""".strip()


def parse_chat_id(raw_value: str):
    if not raw_value:
        raise ValueError("ADMIN_ID не указан")

    raw_value = raw_value.strip()

    # Личный чат / группа / канал по числовому ID
    if raw_value.lstrip("-").isdigit():
        return int(raw_value)

    # Канал по username, например @mrpl_channel
    if raw_value.startswith("@"):
        return raw_value

    raise ValueError(
        "ADMIN_ID должен быть числом (личный Telegram ID) "
        "или @channelusername для канала"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(WELCOME_TEXT)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(
            "Отправьте заявку одним сообщением по шаблону из /start"
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user = update.effective_user
    message = update.message

    username = f"@{user.username}" if user and user.username else "без username"
    first_name = user.first_name if user and user.first_name else "-"
    user_id = user.id if user else "-"

    header = (
        "📩 Новая заявка MRPL Club\n\n"
        f"Имя в Telegram: {first_name}\n"
        f"Username: {username}\n"
        f"Telegram ID: {user_id}\n\n"
        "Сообщение:\n"
    )

    try:
        admin_chat_id = parse_chat_id(ADMIN_ID)

        if message.text:
            text_to_send = header + message.text
        else:
            text_to_send = header + "Пользователь отправил неподдерживаемый тип сообщения."

        await context.bot.send_message(
            chat_id=admin_chat_id,
            text=text_to_send
        )

        await message.reply_text(
            "Спасибо! Ваша заявка принята ❤️\n\n"
            "Менеджер MRPL Club свяжется с вами."
        )

    except Exception as e:
        logger.exception("Ошибка при обработке заявки: %s", e)
        await message.reply_text(
            "Не удалось отправить заявку. Попробуйте позже."
        )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.exception("Unhandled exception: %s", context.error)


def main():
    if not BOT_TOKEN:
        raise ValueError("Не найдена переменная окружения BOT_TOKEN")

    if not ADMIN_ID:
        raise ValueError("Не найдена переменная окружения ADMIN_ID")

    logger.info("Запуск бота...")
    logger.info("ADMIN_ID: %s", ADMIN_ID)

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
