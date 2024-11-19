from telebot import TeleBot
from utils.keyboard import get_settings_keyboard
from database.users import get_user_films_count, set_user_films_count

def register_handlers(bot: TeleBot):
    @bot.message_handler(func=lambda message: message.text == '⚙️ Настройки')
    def settings(message):
        markup = get_settings_keyboard()
        current_count = get_user_films_count(message.from_user.id)
        
        bot.reply_to(
            message,
            f"Текущее количество фильмов в выдаче: {current_count}\n"
            "Выберите новое количество фильмов для отображения:",
            reply_markup=markup
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith('set_films_count_'))
    def callback_films_count(call):
        count = int(call.data.split('_')[-1])
        user_id = call.from_user.id
        
        set_user_films_count(user_id, count)
        
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"✅ Установлено количество фильмов в выдаче: {count}"
        )