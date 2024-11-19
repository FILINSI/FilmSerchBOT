from telebot import TeleBot, types
import requests
import random
from config import API_KEY, GENRES
from database.users import add_shown_film, clear_shown_films, is_film_shown
from utils.keyboard import get_year_range_keyboard

def register_handlers(bot: TeleBot):
    # Сохраняем выбор пользователя
    user_choices = {}

    @bot.message_handler(func=lambda message: message.text == '🎲 Случайный фильм')
    def random_film_menu(message):
        # Очищаем предыдущий выбор пользователя
        user_choices[message.chat.id] = {
            'genre': None, 
            'year': None
        }
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        random_button = types.InlineKeyboardButton(
            "🎲 Любой фильм", 
            callback_data='random_any'
        )
        genres_button = types.InlineKeyboardButton(
            "🎭 Выбрать жанр", 
            callback_data='show_genres'
        )
        year_button = types.InlineKeyboardButton(
            "📅 Выбрать период", 
            callback_data='show_years'
        )
        markup.add(random_button)
        markup.add(genres_button, year_button)
        
        bot.reply_to(
            message,
            "Выберите параметры поиска:",
            reply_markup=markup
        )

    @bot.callback_query_handler(func=lambda call: call.data == 'show_genres')
    def show_genres(call):
        markup = types.InlineKeyboardMarkup(row_width=2)
        genre_buttons = [
            types.InlineKeyboardButton(
                name, 
                callback_data=f'set_genre_{id}'
            ) for id, name in GENRES.items()
        ]
        back_button = types.InlineKeyboardButton("◀️ Назад", callback_data='back_to_menu')
        markup.add(*genre_buttons)
        markup.add(back_button)
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Выберите жанр:",
            reply_markup=markup
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith('set_genre_'))
    def handle_genre_selection(call):
        genre_id = call.data.split('_')[2]
        user_choices[call.message.chat.id]['genre'] = genre_id
        
        show_current_filters(call.message, call.message.message_id)

    @bot.callback_query_handler(func=lambda call: call.data == 'show_years')
    def show_years(call):
        markup = get_year_range_keyboard()
        back_button = types.InlineKeyboardButton("◀️ Назад", callback_data='back_to_menu')
        markup.add(back_button)
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Выберите период:",
            reply_markup=markup
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith('year_'))
    def handle_year_selection(call):
        year_range = call.data.split('_')[1]
        user_choices[call.message.chat.id]['year'] = year_range
        
        show_current_filters(call.message, call.message.message_id)

    @bot.callback_query_handler(func=lambda call: call.data == 'back_to_menu')
    def back_to_menu(call):
        random_film_menu(call.message)

    @bot.callback_query_handler(func=lambda call: call.data == 'search_with_filters')
    def search_with_filters(call):
        chat_id = call.message.chat.id
        choices = user_choices.get(chat_id, {})
        genre_id = choices.get('genre')
        year_range = choices.get('year')
        
        get_random_film(call.message, genre_id, year_range)

    def show_current_filters(message, message_id):
        chat_id = message.chat.id
        choices = user_choices.get(chat_id, {})
        genre_id = choices.get('genre')
        year_range = choices.get('year')
        
        genre_name = GENRES.get(genre_id, 'Не выбран') if genre_id else 'Не выбран'
        year_text = year_range if year_range else 'Не выбран'
        if year_text == 'any':
            year_text = 'Любой'
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        genres_button = types.InlineKeyboardButton(
            "🎭 Выбрать жанр", 
            callback_data='show_genres'
        )
        year_button = types.InlineKeyboardButton(
            "📅 Выбрать период", 
            callback_data='show_years'
        )
        search_button = types.InlineKeyboardButton(
            "🔍 Искать", 
            callback_data='search_with_filters'
        )
        back_button = types.InlineKeyboardButton(
            "◀️ Назад", 
            callback_data='back_to_menu'
        )
        
        markup.add(genres_button, year_button)
        markup.add(search_button)
        markup.add(back_button)
        
        text = (
            "Текущие фильтры:\n"
            f"🎭 Жанр: {genre_name}\n"
            f"📅 Период: {year_text}\n\n"
            "Выберите действие:"
        )
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=markup
        )

    def get_random_film(message, genre_id=None, year_range=None):
        headers = {
            'X-API-KEY': API_KEY,
            'Content-Type': 'application/json',
        }
        
        try:
            # Формируем URL в зависимости от наличия жанра и года
            if genre_id or year_range:
                # Если есть фильтры, используем их
                if year_range and year_range != 'any':
                    start_year, end_year = map(int, year_range.split('-'))
                else:
                    start_year, end_year = 1900, 2024

                url = 'https://kinopoiskapiunofficial.tech/api/v2.2/films'
                params = {
                    'order': 'RATING',
                    'type': 'ALL',
                    'ratingFrom': 0,
                    'ratingTo': 10,
                    'yearFrom': start_year,
                    'yearTo': end_year,
                    'page': 1
                }
                
                if genre_id:
                    params['genres'] = genre_id
            else:
                # Если фильтров нет, берем из топ-250
                url = 'https://kinopoiskapiunofficial.tech/api/v2.2/films/top?type=TOP_250_BEST_FILMS&page=1'
                params = {}

            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            
            if data.get('items') or data.get('films'):
                films = data.get('items') or data.get('films')
                
                # Фильтруем уже показанные фильмы
                cache_key = f"{str(genre_id)}_{year_range}"
                available_films = [
                    film for film in films 
                    if not is_film_shown(
                        message.chat.id, 
                        cache_key,
                        film.get('kinopoiskId') or film.get('filmId')
                    )
                ]
                
                # Если все фильмы показаны, очищаем историю
                if not available_films:
                    clear_shown_films(message.chat.id, cache_key)
                    available_films = films
                
                film = random.choice(available_films)
                film_id = film.get('kinopoiskId') or film.get('filmId')
                
                # Добавляем фильм в показанные
                add_shown_film(message.chat.id, cache_key, film_id)
                
                # Плучаем детальную информацию о фильме
                details_response = requests.get(
                    f'https://kinopoiskapiunofficial.tech/api/v2.2/films/{film_id}',
                    headers=headers
                )
                film_details = details_response.json()
                
                film_title = film_details.get('nameRu') or film_details.get('nameOriginal')
                film_year = film_details.get('year', "Год не указан")
                poster_url = film_details.get('posterUrl')
                film_length = film_details.get('filmLength')  # Получаем длительность
                
                kp_rating = film_details.get('ratingKinopoisk', 'Нет оценки')
                imdb_rating = film_details.get('ratingImdb', 'Нет оценки')
                description = film_details.get('description', '')
                
                # Получаем тип (фильм/сериал) и информацию о сезонах
                film_type = film_details.get('type', '').upper()
                seasons_count = None
                
                # Если это сериал, получаем информацию о сезонах
                if film_type == 'TV_SERIES':
                    try:
                        seasons_response = requests.get(
                            f'https://kinopoiskapiunofficial.tech/api/v2.2/films/{film_id}/seasons',
                            headers=headers
                        )
                        seasons_data = seasons_response.json()
                        if seasons_data.get('items'):
                            seasons_count = len(seasons_data['items'])
                    except Exception as e:
                        print(f"Error getting seasons info: {e}")
                
                # Получаем жанры фильма
                genres = [genre['genre'] for genre in film_details.get('genres', [])]
                genres_str = ', '.join(genres) if genres else 'Не указаны'
                
                watch_url = f"https://www.kinopoisk.vip/film/{film_id}/"
                
                markup = types.InlineKeyboardMarkup(row_width=2)
                watch_button = types.InlineKeyboardButton("Смотреть", url=watch_url)
                next_button = types.InlineKeyboardButton(
                    "🎲 Следующий случайный", 
                    callback_data=f'next_random_{genre_id or "any"}_{year_range or "any"}'
                )
                markup.add(watch_button, next_button)
                
                # Формируем текст сообщения
                message_text = (
                    f"🎬 {film_title}\n"
                    f"📅 {film_year}\n"
                    f"🎭 Жанры: {genres_str}\n"
                    f"⭐️ Рейтинг Кинопоиск: {kp_rating}\n"
                    f"📊 Рейтинг IMDb: {imdb_rating}"
                )
                
                # Добавляем информацию о сезонах для сериала или длительность для фильма
                if film_type == 'TV_SERIES':
                    seasons_text = f"\n📺 Сезонов: {seasons_count}" if seasons_count else "\n📺 Сериал"
                    message_text += seasons_text
                elif film_length:  # Если есть длительность
                    message_text += f"\n⏱️ Длительность: {film_length} мин."
                
                # Добавляем описание, если оно есть
                if description:
                    message_text += f"\n\n📝 {description[:200]}..." if len(description) > 200 else f"\n\n📝 {description}"
                
                if poster_url:
                    try:
                        bot.send_photo(
                            message.chat.id,
                            poster_url,
                            caption=message_text,
                            reply_markup=markup
                        )
                    except Exception as e:
                        print(f"Error sending photo: {e}")
                        bot.send_message(
                            message.chat.id,
                            message_text,
                            reply_markup=markup
                        )
                else:
                    bot.send_message(
                        message.chat.id,
                        message_text,
                        reply_markup=markup
                    )
            else:
                bot.send_message(
                    message.chat.id,
                    "К сожалению, не удалось найти фильм. Попробуйте другой жанр."
                )
                
        except Exception as e:
            print(f"Error: {e}")
            bot.send_message(
                message.chat.id,
                "Произошла ошибка при поиске случайного фильма. Попробуйте еще раз."
            )

    # Обновленный обработчик для кнопки "Следующий случайный"
    @bot.callback_query_handler(func=lambda call: call.data.startswith('next_random_'))
    def handle_next_random(call):
        try:
            # Разбираем callback_data
            parts = call.data.split('_')
            if len(parts) >= 3:  # next_random_genre_year
                genre_id = parts[2]
                year_range = parts[3]
                
                # Преобразуем 'any' в None
                genre_id = None if genre_id == 'any' else genre_id
                year_range = None if year_range == 'any' else year_range
                
                # Получаем следующий случайный фильм
                get_random_film(call.message, genre_id, year_range)
            else:
                # Если формат неверный, показываем случайный фильм без фильтров
                get_random_film(call.message)
                
        except Exception as e:
            print(f"Error in handle_next_random: {e}")
            bot.answer_callback_query(
                call.id,
                text="Произошла ошибка. Попробуйте еще раз."
            )

    @bot.callback_query_handler(func=lambda call: call.data == 'random_any')
    def handle_random_any(call):
        try:
            # Очищаем выбор пользователя для случайного поиска
            user_choices[call.message.chat.id] = {
                'genre': None,
                'year': None
            }
            
            # Получаем случайный фильм без фильтров
            get_random_film(call.message)
            
            # Отвечаем на callback
            bot.answer_callback_query(call.id)
            
        except Exception as e:
            print(f"Error in handle_random_any: {e}")
            bot.answer_callback_query(
                call.id,
                text="Произошла ошибка. Попробуйте еще раз."
            )
