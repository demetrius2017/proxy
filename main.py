from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import logging
from user_manager import save_user_id, export_user_ids

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Константы
WEB_APP_URL = "https://appproxy.vercel.app/"
ANDROID_TEXT = "Открыть App Launcher для Android"
IOS_TEXT = "Инструкция для iPhone"


# Список ID администраторов (замените на реальные ID)
ADMIN_IDS = [138503110, 5882393609]  # Замените эти числа на реальные ID администраторов

async def set_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in ADMIN_IDS:
        context.user_data['is_admin'] = True
        await update.message.reply_text("Вы успешно авторизованы как администратор.")
    else:
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")

# Обновленная функция export_users с проверкой на администратора
async def export_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in ADMIN_IDS and context.user_data.get('is_admin', False):
        output_file = export_user_ids()
        await update.message.reply_document(document=open(output_file, 'rb'), filename=output_file)
    else:
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")

async def send_start_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Сохраняем ID пользователя
    user_id = update.effective_user.id
    save_user_id(user_id)

    # Обновление команд меню
    commands = [
        BotCommand("start", "Начать работу с ботом"),
        BotCommand("help", "Получить помощь"),
        BotCommand("about", "О нашем сервисе"),
        BotCommand("export_users", "Экспорт ID пользователей (только для админов)")
    ]
    await context.bot.set_my_commands(commands)

    # Создание клавиатуры
    keyboard = [
        [InlineKeyboardButton(text=ANDROID_TEXT, web_app=WebAppInfo(url=WEB_APP_URL))],
        [InlineKeyboardButton(text=IOS_TEXT, callback_data="ios_instructions")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Текст сообщения
    message_text = "Добро пожаловать в App Launcher! 👋\n\nВыберите вашу платформу:"

    # Отправка или редактирование сообщения
    if update.message:
        await update.message.reply_text(text=message_text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text(text=message_text, reply_markup=reply_markup)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_start_message(update, context)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "ios_instructions":
        instructions = (
            "Инструкция для пользователей iPhone:\n\n"
            "1. Зажмите и удерживайте эту ссылку: https://appproxy.vercel.app/\n"
            "2. Открыть в ...\n"
            "3. Выберете браузер Chrome\n\n"
            "Готово! Теперь вы можете использовать App Launcher на вашем iPhone."
        )
        await query.edit_message_text(
            text=instructions,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="« Назад", callback_data="back_to_start")]])
        )
    elif query.data == "back_to_start":
        await send_start_message(update, context)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Помощь по использованию App Launcher:\n\n"
        "• Для Android: нажмите кнопку 'Открыть App Launcher для Android'\n"
        "• Для iPhone: следуйте инструкциям, нажав на 'Инструкция для iPhone'\n\n"
        "Если у вас возникли проблемы, пожалуйста, свяжитесь с нашей поддержкой."
    )
    await update.message.reply_text(help_text)

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    about_text = (
        "О нашем сервисе App Launcher:\n\n"
        "App Launcher - это удобный инструмент для быстрого доступа к популярным веб-приложениям. "
        "Мы предоставляем простой и безопасный способ обхода ограничений и доступа к вашим любимым сервисам.\n\n"
        "Наша миссия - сделать интернет доступным для всех!"
    )
    await update.message.reply_text(about_text)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception while handling an update: {context.error}")

def main():
    # Инициализация бота
    application = ApplicationBuilder().token('6740830002:AAFcw7PqsWgGp4cJna24vofPtU1P2dCT4yE').build()

    # Добавляем обработчики
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('about', about_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(CommandHandler('export_users', export_users))
    application.add_handler(CommandHandler('set_admin', set_admin))

    # Добавляем обработчик ошибок
    application.add_error_handler(error_handler)

    # Запуск бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()