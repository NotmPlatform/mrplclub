
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "7964857997"))

WELCOME_TEXT = """
MRPL Club - знакомства в Мариуполе

Мы проводим вечера знакомств, где за один вечер можно познакомиться с 10-15 новыми людьми.

Форматы встреч:
• быстрые свидания
• свидания вслепую
• знакомства через игры и общение

Места на мероприятия ограничены.
"""

HOW_TEXT = """
Как проходит вечер MRPL Club:

• 10-15 участников
• общение по 5 минут
• после сигнала пары меняются
• за вечер знакомитесь почти со всеми

В конце вечера вы отмечаете симпатии.
Если симпатия взаимная - участники получают контакты.
"""

FORM_TEXT = """
Отправьте заявку по форме:

Имя:
Возраст:
Город:
Телефон:
С кем хотите познакомиться (возраст):

Укажите диапазон возраста, например: 24-32

Пример:

Имя: Алексей
Возраст: 29
Город: Мариуполь
Телефон: +7XXXXXXXXXX
С кем хотите познакомиться (возраст): 24-32
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Подать заявку", callback_data="apply")],
        [InlineKeyboardButton("Как проходят встречи", callback_data="how")]
    ]
    await update.message.reply_text(
        WELCOME_TEXT,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "apply":
        await query.message.reply_text(FORM_TEXT)

    if query.data == "how":
        keyboard = [[InlineKeyboardButton("Подать заявку", callback_data="apply")]]
        await query.message.reply_text(
            HOW_TEXT,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def handle_application(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    admin_message = f"Новая заявка MRPL Club:\n\n{text}"

    await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message)

    await update.message.reply_text(
        "Спасибо! Ваша заявка принята. Менеджер MRPL Club свяжется с вами."
    )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_application))

    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
