from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler

async def start(update: Update, context):
    # Создаем правильный формат для клавиатуры
    keyboard = [
        [InlineKeyboardButton(text="для Android жми", web_app=WebAppInfo(url="https://appproxy.vercel.app/"))]
    ]
    
    # Создаем объект InlineKeyboardMarkup с кнопками
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправляем сообщение с кнопкой и ссылкой
    await update.message.reply_text(
        text="Для iPhone, открыть ссылку через Chrome браузер (для этого нажав и удерживая ссылку ниже выберрете отрыть в Chrome): "
             "https://appproxy.vercel.app/",
        reply_markup=reply_markup
    )

# Инициализация бота
application = ApplicationBuilder().token('6740830002:AAFcw7PqsWgGp4cJna24vofPtU1P2dCT4yE').build()

# Добавляем обработчик команды /start
application.add_handler(CommandHandler('start', start))

# Запуск бота
application.run_polling()
