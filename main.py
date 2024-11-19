import telebot
from config import BOT_TOKEN
from handlers import start, status, settings, search, random_film

# Инициализация бота
bot = telebot.TeleBot(BOT_TOKEN)

# Регистрация всех обработчиков
def register_handlers():
    start.register_handlers(bot)
    status.register_handlers(bot)
    settings.register_handlers(bot)
    search.register_handlers(bot)
    random_film.register_handlers(bot)

if __name__ == '__main__':
    # Регистрируем обработчики
    register_handlers()
    # Запускаем бота
    bot.polling(none_stop=True)