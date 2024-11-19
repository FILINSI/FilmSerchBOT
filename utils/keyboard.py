from telebot import types

def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    status_button = types.KeyboardButton('📊 Статус системы')
    settings_button = types.KeyboardButton('⚙️ Настройки')
    random_button = types.KeyboardButton('🎲 Случайный фильм')
    search_button = types.KeyboardButton('🔍 Поиск фильма')
    markup.add(status_button, settings_button)
    markup.add(random_button, search_button)
    return markup

def get_settings_keyboard():
    markup = types.InlineKeyboardMarkup()
    for i in [3, 5, 7, 10]:
        callback_data = f'set_films_count_{i}'
        button = types.InlineKeyboardButton(text=f'{i} фильмов', callback_data=callback_data)
        markup.add(button)
    return markup

def get_year_range_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    ranges = [
        ("До 1980", "1900-1980"),
        ("1980-2000", "1980-2000"),
        ("2000-2010", "2000-2010"),
        ("2010-2020", "2010-2020"),
        ("2020+", "2020-2024"),
        ("Любой год", "any")
    ]
    
    buttons = [
        types.InlineKeyboardButton(text=name, callback_data=f'year_{value}')
        for name, value in ranges
    ]
    markup.add(*buttons)
    return markup