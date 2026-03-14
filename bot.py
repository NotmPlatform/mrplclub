import os
import re
import logging

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния диалога
(
    START_MENU,
    NAME,
    AGE,
    GENDER,
    CITY_CONFIRM,
    CITY_INPUT,
    PHONE,
    PARTNER_AGE_FROM,
    PARTNER_AGE_TO,
    CONFIRM,
    EDIT_FIELD,
) = range(11)


def parse_chat_id(value: str):
    value = value.strip()
    if value.lstrip("-").isdigit():
        return int(value)
    if value.startswith("@"):
        return value
    raise ValueError("ADMIN_ID должен быть числом или @channelusername")


def start_keyboard():
    return ReplyKeyboardMarkup(
        [["Начать анкету"]],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def gender_keyboard():
    return ReplyKeyboardMarkup(
        [["М", "Ж"]],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def city_confirm_keyboard():
    return ReplyKeyboardMarkup(
        [["Да", "Изменить"]],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def confirm_keyboard():
    return ReplyKeyboardMarkup(
        [["Подтвердить и отправить"], ["Изменить анкету"]],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def edit_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["Имя", "Возраст"],
            ["Пол", "Город"],
            ["Телефон", "Возраст партнера"],
            ["Назад"]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def gender_to_text(value: str) -> str:
    if value == "М":
        return "Мужской"
    if value == "Ж":
        return "Женский"
    return "-"


def phone_is_valid(phone: str) -> bool:
    return bool(re.fullmatch(r"\+7\d{10}", phone))


def build_summary(data: dict) -> str:
    return (
        "Проверьте вашу анкету:\n\n"
        f"Имя: {data.get('name', '-')}\n"
        f"Возраст: {data.get('age', '-')}\n"
        f"Пол: {gender_to_text(data.get('gender', '-'))}\n"
        f"Город: {data.get('city', '-')}\n"
        f"Телефон: {data.get('phone', '-')}\n"
        f"Желаемый возраст партнера: "
        f"{data.get('partner_age_from', '-')}–{data.get('partner_age_to', '-')}"
    )


async def show_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        build_summary(context.user_data),
        reply_markup=confirm_keyboard()
    )
    return CONFIRM


def clear_edit_mode(context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("edit_mode", None)
    context.user_data.pop("edit_field", None)


def set_edit_mode(context: ContextTypes.DEFAULT_TYPE, field_name: str):
    context.user_data["edit_mode"] = True
    context.user_data["edit_field"] = field_name


def is_editing(context: ContextTypes.DEFAULT_TYPE, field_name: str) -> bool:
    return (
        context.user_data.get("edit_mode") is True
        and context.user_data.get("edit_field") == field_name
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    welcome_text = (
        "💘 <b>MRPL Club — знакомства в Мариуполе</b>\n\n"
        "Мы проводим вечера знакомств, где за один вечер можно познакомиться "
        "с новыми людьми в комфортной атмосфере.\n\n"
        "В анкете будет всего несколько коротких вопросов.\n"
        "Нажмите кнопку ниже, чтобы начать."
    )

    await update.message.reply_text(
        welcome_text,
        parse_mode="HTML",
        reply_markup=start_keyboard()
    )
    return START_MENU


async def start_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text != "Начать анкету":
        await update.message.reply_text(
            "Пожалуйста, нажмите кнопку «Начать анкету».",
            reply_markup=start_keyboard()
        )
        return START_MENU

    await update.message.reply_text(
        "Введите ваше имя:",
        reply_markup=ReplyKeyboardRemove()
    )
    return NAME


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "Анкета отменена. Чтобы начать заново, нажмите /start",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if len(text) < 2:
        await update.message.reply_text("Введите корректное имя:")
        return NAME

    context.user_data["name"] = text

    if is_editing(context, "name"):
        clear_edit_mode(context)
        return await show_summary(update, context)

    await update.message.reply_text("Введите ваш возраст:")
    return AGE


async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if not text.isdigit():
        await update.message.reply_text("Возраст нужно ввести цифрами. Например: 29")
        return AGE

    age = int(text)
    if age < 18 or age > 80:
        await update.message.reply_text("Введите корректный возраст от 18 до 80:")
        return AGE

    context.user_data["age"] = age

    if is_editing(context, "age"):
        clear_edit_mode(context)
        return await show_summary(update, context)

    await update.message.reply_text(
        "Укажите ваш пол:",
        reply_markup=gender_keyboard()
    )
    return GENDER


async def get_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text not in ["М", "Ж"]:
        await update.message.reply_text(
            "Пожалуйста, выберите пол кнопкой ниже:",
            reply_markup=gender_keyboard()
        )
        return GENDER

    context.user_data["gender"] = text

    if is_editing(context, "gender"):
        clear_edit_mode(context)
        return await show_summary(update, context)

    await update.message.reply_text(
        "Ваш город — Мариуполь?",
        reply_markup=city_confirm_keyboard()
    )
    return CITY_CONFIRM


async def confirm_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text == "Да":
        context.user_data["city"] = "Мариуполь"

        if is_editing(context, "city"):
            clear_edit_mode(context)
            return await show_summary(update, context)

        await update.message.reply_text(
            "Введите номер телефона в формате +7XXXXXXXXXX",
            reply_markup=ReplyKeyboardRemove()
        )
        return PHONE

    if text == "Изменить":
        await update.message.reply_text(
            "Введите ваш город:",
            reply_markup=ReplyKeyboardRemove()
        )
        return CITY_INPUT

    await update.message.reply_text(
        "Пожалуйста, нажмите кнопку: Да или Изменить",
        reply_markup=city_confirm_keyboard()
    )
    return CITY_CONFIRM


async def input_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if len(text) < 2:
        await update.message.reply_text("Введите корректное название города:")
        return CITY_INPUT

    context.user_data["city"] = text

    if is_editing(context, "city"):
        clear_edit_mode(context)
        return await show_summary(update, context)

    await update.message.reply_text("Введите номер телефона в формате +7XXXXXXXXXX")
    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().replace(" ", "")

    if not phone_is_valid(text):
        await update.message.reply_text(
            "Неверный формат номера.\n"
            "Введите телефон строго в формате +7XXXXXXXXXX"
        )
        return PHONE

    context.user_data["phone"] = text

    if is_editing(context, "phone"):
        clear_edit_mode(context)
        return await show_summary(update, context)

    await update.message.reply_text("Введите желаемый возраст партнера: от")
    return PARTNER_AGE_FROM


async def get_partner_age_from(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if not text.isdigit():
        await update.message.reply_text("Введите возраст цифрами. Например: 24")
        return PARTNER_AGE_FROM

    age_from = int(text)
    if age_from < 18 or age_from > 80:
        await update.message.reply_text("Введите корректный возраст от 18 до 80:")
        return PARTNER_AGE_FROM

    context.user_data["partner_age_from"] = age_from
    await update.message.reply_text("Введите желаемый возраст партнера: до")
    return PARTNER_AGE_TO


async def get_partner_age_to(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if not text.isdigit():
        await update.message.reply_text("Введите возраст цифрами. Например: 32")
        return PARTNER_AGE_TO

    age_to = int(text)
    age_from = context.user_data.get("partner_age_from")

    if age_to < 18 or age_to > 80:
        await update.message.reply_text("Введите корректный возраст от 18 до 80:")
        return PARTNER_AGE_TO

    if age_from is not None and age_to < age_from:
        await update.message.reply_text(
            f"Возраст 'до' не может быть меньше возраста 'от' ({age_from}).\n"
            "Введите корректное значение:"
        )
        return PARTNER_AGE_TO

    context.user_data["partner_age_to"] = age_to

    if is_editing(context, "partner_age"):
        clear_edit_mode(context)

    return await show_summary(update, context)


async def confirm_form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text == "Подтвердить и отправить":
        user = update.effective_user
        username = f"@{user.username}" if user and user.username else "без username"
        first_name = user.first_name if user and user.first_name else "-"
        user_id = user.id if user else "-"

        msg = (
            "📩 Новая заявка MRPL Club\n\n"
            f"Имя в Telegram: {first_name}\n"
            f"Username: {username}\n"
            f"Telegram ID: {user_id}\n\n"
            "Анкета:\n"
            f"Имя: {context.user_data.get('name', '-')}\n"
            f"Возраст: {context.user_data.get('age', '-')}\n"
            f"Пол: {gender_to_text(context.user_data.get('gender', '-'))}\n"
            f"Город: {context.user_data.get('city', '-')}\n"
            f"Телефон: {context.user_data.get('phone', '-')}\n"
            f"Желаемый возраст партнера: "
            f"{context.user_data.get('partner_age_from', '-')}"
            f"–{context.user_data.get('partner_age_to', '-')}"
        )

        try:
            admin_chat_id = context.application.bot_data["admin_chat_id"]
            await context.bot.send_message(chat_id=admin_chat_id, text=msg)

            await update.message.reply_text(
                "Спасибо! Ваша заявка принята ❤️\n\n"
                "Менеджер MRPL Club свяжется с вами.",
                reply_markup=ReplyKeyboardRemove()
            )
        except Exception as e:
            logger.exception("Ошибка при отправке анкеты: %s", e)
            await update.message.reply_text(
                "Не удалось отправить заявку. Попробуйте позже.",
                reply_markup=ReplyKeyboardRemove()
            )

        context.user_data.clear()
        return ConversationHandler.END

    if text == "Изменить анкету":
        await update.message.reply_text(
            "Что хотите изменить?",
            reply_markup=edit_keyboard()
        )
        return EDIT_FIELD

    await update.message.reply_text(
        "Пожалуйста, нажмите кнопку ниже:",
        reply_markup=confirm_keyboard()
    )
    return CONFIRM


async def edit_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text == "Имя":
        set_edit_mode(context, "name")
        await update.message.reply_text(
            "Введите новое имя:",
            reply_markup=ReplyKeyboardRemove()
        )
        return NAME

    if text == "Возраст":
        set_edit_mode(context, "age")
        await update.message.reply_text(
            "Введите новый возраст:",
            reply_markup=ReplyKeyboardRemove()
        )
        return AGE

    if text == "Пол":
        set_edit_mode(context, "gender")
        await update.message.reply_text(
            "Выберите пол:",
            reply_markup=gender_keyboard()
        )
        return GENDER

    if text == "Город":
        set_edit_mode(context, "city")
        await update.message.reply_text(
            "Ваш город — Мариуполь?",
            reply_markup=city_confirm_keyboard()
        )
        return CITY_CONFIRM

    if text == "Телефон":
        set_edit_mode(context, "phone")
        await update.message.reply_text(
            "Введите номер телефона в формате +7XXXXXXXXXX",
            reply_markup=ReplyKeyboardRemove()
        )
        return PHONE

    if text == "Возраст партнера":
        set_edit_mode(context, "partner_age")
        await update.message.reply_text(
            "Введите желаемый возраст партнера: от",
            reply_markup=ReplyKeyboardRemove()
        )
        return PARTNER_AGE_FROM

    if text == "Назад":
        clear_edit_mode(context)
        return await show_summary(update, context)

    await update.message.reply_text(
        "Пожалуйста, выберите поле кнопкой ниже:",
        reply_markup=edit_keyboard()
    )
    return EDIT_FIELD


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.exception("Необработанная ошибка: %s", context.error)


def main():
    bot_token = os.getenv("BOT_TOKEN")
    admin_id_raw = os.getenv("ADMIN_ID")

    if not bot_token:
        raise ValueError("Не найдена переменная окружения BOT_TOKEN")

    if not admin_id_raw:
        raise ValueError("Не найдена переменная окружения ADMIN_ID")

    admin_chat_id = parse_chat_id(admin_id_raw)

    app = ApplicationBuilder().token(bot_token).build()
    app.bot_data["admin_chat_id"] = admin_chat_id

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
        ],
        states={
            START_MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, start_menu_handler),
            ],
            NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_name),
            ],
            AGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_age),
            ],
            GENDER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_gender),
            ],
            CITY_CONFIRM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_city),
            ],
            CITY_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, input_city),
            ],
            PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone),
            ],
            PARTNER_AGE_FROM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_partner_age_from),
            ],
            PARTNER_AGE_TO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_partner_age_to),
            ],
            CONFIRM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_form),
            ],
            EDIT_FIELD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, edit_field),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_error_handler(error_handler)

    logger.info("Bot started...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
