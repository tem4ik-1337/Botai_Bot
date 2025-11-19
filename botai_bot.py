import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "8246248813:AAGK82GNL1f-KE_5W-czf2IePnEXwwazQxkUR_BOT_TOKEN_HERE"

# Состояния для ConversationHandler
SELECT_PRESET, SELECT_MODE = range(2)

# Временное хранилище пресетов
user_presets = {}

# Создаем главное меню
def get_main_keyboard():
    keyboard = [
        [KeyboardButton("help"), KeyboardButton("Ботать")],
        [KeyboardButton("Создать пресет")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Меню для выбора пресета
def get_preset_keyboard(user_id):
    if user_id in user_presets and user_presets[user_id]:
        keyboard = []
        for preset_name in user_presets[user_id].keys():
            keyboard.append([KeyboardButton(preset_name)])
        keyboard.append([KeyboardButton("↩️ Назад")])
    else:
        keyboard = [[KeyboardButton("↩️ Назад")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Меню для выбора режима
def get_mode_keyboard():
    keyboard = [
        [KeyboardButton("Блиц"), KeyboardButton("Подробный")],
        [KeyboardButton("↩️ Назад")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    welcome_text = f"Привет, {user.first_name}! 👋\n\nВыберите действие из меню:"
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_keyboard()
    )

# Обработка кнопки "help"
async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📋 **Помощь по боту:**

🤖 **Основные функции:**
• *Ботать* - запустить процесс с выбранным пресетом
• *Создать пресет* - создать новый пресет настроек
• *help* - показать эту справку

🔄 **Процесс работы:**
1. Создайте пресет через кнопку "Создать пресет"
2. Нажмите "Ботать" и выберите созданный пресет
3. Выберите режим работы: "Блиц" или "Подробный"

🎯 **Режимы работы:**
• *Блиц* - быстрая обработка
• *Подробный* - детальный анализ с расширенными настройками

*Для связи с разработчиком: @username*
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

# Обработка кнопки "Создать пресет"
async def create_preset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    # Инициализируем хранилище пресетов для пользователя, если его нет
    if user_id not in user_presets:
        user_presets[user_id] = {}
    
    # Создаем пример пресета
    preset_name = f"Пресет_{len(user_presets[user_id]) + 1}"
    user_presets[user_id][preset_name] = {
        "settings": "стандартные настройки",
        "created_at": "2024-01-01"
    }
    
    await update.message.reply_text(
        f"✅ Создан новый пресет: *{preset_name}*\n\n"
        "Теперь вы можете выбрать его в меню 'Ботать'",
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

# Начало процесса "Ботать"
async def start_botting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    # Проверяем есть ли пресеты у пользователя
    if user_id not in user_presets or not user_presets[user_id]:
        await update.message.reply_text(
            "❌ У вас нет созданных пресетов.\n"
            "Сначала создайте пресет через меню 'Создать пресет'",
            reply_markup=get_main_keyboard()
        )
        return ConversationHandler.END
    
    await update.message.reply_text(
        "📁 Выберите пресет для работы:",
        reply_markup=get_preset_keyboard(user_id)
    )
    return SELECT_PRESET

# Обработка выбора пресета
async def select_preset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    preset_name = update.message.text
    
    if preset_name == "↩️ Назад":
        await update.message.reply_text(
            "Возврат в главное меню:",
            reply_markup=get_main_keyboard()
        )
        return ConversationHandler.END
    
    # Проверяем существование пресета
    if user_id in user_presets and preset_name in user_presets[user_id]:
        context.user_data['selected_preset'] = preset_name
        await update.message.reply_text(
            f"✅ Выбран пресет: *{preset_name}*\n\n"
            "Теперь выберите режим работы:",
            parse_mode='Markdown',
            reply_markup=get_mode_keyboard()
        )
        return SELECT_MODE
    else:
        await update.message.reply_text(
            "❌ Пресет не найден. Выберите пресет из списка:",
            reply_markup=get_preset_keyboard(user_id)
        )
        return SELECT_PRESET

# Обработка выбора режима
async def select_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = update.message.text
    preset_name = context.user_data.get('selected_preset', 'неизвестный')
    
    if mode == "↩️ Назад":
        user_id = update.message.from_user.id
        await update.message.reply_text(
            "Выберите пресет:",
            reply_markup=get_preset_keyboard(user_id)
        )
        return SELECT_PRESET
    
    if mode in ["Блиц", "Подробный"]:
        # Здесь запускается основной процесс бота
        if mode == "Блиц":
            process_text = "🚀 Запущен *Блиц-режим* с пресетом"
            details = "Быстрая обработка данных в ускоренном темпе."
        else:
            process_text = "🔍 Запущен *Подробный режим* с пресетом"
            details = "Детальный анализ с полной диагностикой."
        
        await update.message.reply_text(
            f"{process_text} *{preset_name}*\n\n"
            f"{details}\n\n"
            "⏳ Процесс запущен...",
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
        
        # Здесь можно добавить логику обработки
        
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            "Пожалуйста, выберите режим из предложенных:",
            reply_markup=get_mode_keyboard()
        )
        return SELECT_MODE

# Отмена диалога
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Диалог отменен.",
        reply_markup=get_main_keyboard()
    )
    return ConversationHandler.END

# Обработка текстовых сообщений главного меню
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "help":
        await show_help(update, context)
    elif text == "Создать пресет":
        await create_preset(update, context)
    elif text == "Ботать":
        await start_botting(update, context)
    else:
        await update.message.reply_text(
            "Пожалуйста, используйте кнопки меню 👆",
            reply_markup=get_main_keyboard()
        )

# Обработка ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Ошибка: {context.error}")

# Основная функция
def main():
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()

    # ConversationHandler для процесса "Ботать"
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Ботать$"), start_botting)],
        states={
            SELECT_PRESET: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, select_preset)
            ],
            SELECT_MODE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, select_mode)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Обработчик ошибок
    application.add_error_handler(error_handler)

    # Запускаем бота
    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()