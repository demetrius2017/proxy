from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler

async def start(update: Update, context):
    await send_main_message(update, context)

async def send_main_message(update: Update, context):
    keyboard = [
        [InlineKeyboardButton(text="для Android жми", web_app=WebAppInfo(url="https://appproxy.vercel.app/"))]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        text="Для iPhone, открыть ссылку через Chrome браузер (для этого нажав и удерживая ссылку ниже выберите открыть в Chrome): "
             "https://appproxy.vercel.app/",
        reply_markup=reply_markup
    )

async def setup_commands(application):
    commands = [
        BotCommand("start", "Начать работу с ботом"),
    ]
    await application.bot.set_my_commands(commands)

# Инициализация бота
application = ApplicationBuilder().token('6740830002:AAFcw7PqsWgGp4cJna24vofPtU1P2dCT4yE').build()

# Добавляем обработчики команд
application.add_handler(CommandHandler('start', start))
application.add_handler(CommandHandler('restart', restart))

# Настройка команд меню
application.create_task(setup_commands(application))

# Запуск бота
application.run_polling()