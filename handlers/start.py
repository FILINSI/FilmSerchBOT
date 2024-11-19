from telebot import TeleBot
from utils.keyboard import get_main_keyboard

def register_handlers(bot: TeleBot):
    @bot.message_handler(commands=['start'])
    def start(message):
        markup = get_main_keyboard()
        bot.reply_to(message, 
                     "Привет! Я помогу найти фильм на Кинопоиск.\n"
                     "Просто напиши название фильма.\n\n"
                     "Используй меню для настройки бота:", 
                     reply_markup=markup)