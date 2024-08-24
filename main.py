from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler

async def start(update: Update, context):
    # Обновление команд меню
    commands = [
        BotCommand("start", "Начать работу с ботом")
    ]
    await context.bot.set_my_commands(commands)

    # Создание клавиатуры
    keyboard = [
        [InlineKeyboardButton(text="для Android жми", web_app=WebAppInfo(url="https://appproxy.vercel.app/"))]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправка сообщения
    await update.message.reply_text(
        text="Для iPhone, открыть ссылку через Chrome браузер (для этого нажав и удерживая ссылку ниже выберите открыть в Chrome): "
             "https://appproxy.vercel.app/",
        reply_markup=reply_markup
    )

def main():
    # Инициализация бота
    application = ApplicationBuilder().token('6740830002:AAFcw7PqsWgGp4cJna24vofPtU1P2dCT4yE').build()

    # Добавляем обработчик команды start
    application.add_handler(CommandHandler('start', start))

    # Запуск бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()