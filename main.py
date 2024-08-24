from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler

async def start(update: Update, context):
    # Создаем правильный формат для клавиатуры
    keyboard = [
        [InlineKeyboardButton(text="Запуск", web_app=WebAppInfo(url="https://autoproxy-launcher.vercel.app/"))]
    ]
    
    # Создаем объект InlineKeyboardMarkup с кнопками
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправляем сообщение с кнопкой и ссылкой
    await update.message.reply_text(
        text="Для запуска перейдите по кнопке:",
        reply_markup=reply_markup
    )

# Инициализация бота
application = ApplicationBuilder().token('7205474470:AAF5gNWm2mdtAJMbHa5Uj7LWg2y58sgI_NA').build()

# Добавляем обработчик команды /start
application.add_handler(CommandHandler('start', start))

# Запуск бота
application.run_polling()
