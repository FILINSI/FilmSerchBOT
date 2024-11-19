from telebot import TeleBot
from datetime import datetime
from database.users import get_user_films_count

def register_handlers(bot: TeleBot):
    @bot.message_handler(func=lambda message: message.text == '📊 Статус системы')
    def status(message):
        current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        films_count = get_user_films_count(message.from_user.id)
        
        status_message = (
            "🤖 Статус бота:\n"
            f"✅ Бот работает\n"
            f"⏰ Текущее время: {current_time}\n"
            f"🎬 Количество фильмов в выдаче: {films_count}\n"
            f"🔑 API подключен"
        )
        
        bot.reply_to(message, status_message)