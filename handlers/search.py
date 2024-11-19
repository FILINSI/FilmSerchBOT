from telebot import TeleBot, types
import requests
from config import API_KEY
from database.users import get_user_films_count

def register_handlers(bot: TeleBot):
    @bot.message_handler(func=lambda message: message.text == '🔍 Поиск фильма')
    def search_command(message):
        bot.reply_to(
            message,
            "Введите название фильма или сериала для поиска:"
        )

    @bot.message_handler(func=lambda message: not message.text.startswith('/') 
                        and message.text not in ['📊 Статус системы', '⚙️ Настройки', 
                                               '🎲 Случайный фильм', '🔍 Поиск фильма'])
    def search_film(message):
        film_name = message.text
        films_count = get_user_films_count(message.from_user.id)
        
        headers = {
            'X-API-KEY': API_KEY,
            'Content-Type': 'application/json',
        }
        
        try:
            # Поиск фильмов по названию
            response = requests.get(
                f'https://kinopoiskapiunofficial.tech/api/v2.1/films/search-by-keyword?keyword={film_name}',
                headers=headers
            )
            data = response.json()
            
            if data.get('films'):
                for film in data['films'][:films_count]:
                    film_id = film.get('filmId')
                    
                    # Получаем детальную информацию о фильме
                    details_response = requests.get(
                        f'https://kinopoiskapiunofficial.tech/api/v2.2/films/{film_id}',
                        headers=headers
                    )
                    film_details = details_response.json()
                    
                    film_title = film.get('nameRu') or film.get('nameEn')
                    film_year = film.get('year', "Год не указан")
                    poster_url = film.get('posterUrlPreview')
                    film_type = film_details.get('type', '').upper()
                    film_length = film_details.get('filmLength')
                    
                    # Получаем рейтинги
                    kp_rating = film_details.get('ratingKinopoisk', 'Нет оценки')
                    imdb_rating = film_details.get('ratingImdb', 'Нет оценки')
                    
                    # Получаем жанры
                    genres = [genre['genre'] for genre in film_details.get('genres', [])]
                    genres_str = ', '.join(genres) if genres else 'Не указаны'
                    
                    watch_url = f"https://www.kinopoisk.vip/film/{film_id}/"
                    
                    markup = types.InlineKeyboardMarkup()
                    button = types.InlineKeyboardButton("Смотреть", url=watch_url)
                    markup.add(button)
                    
                    message_text = (
                        f"🎬 {film_title}\n"
                        f"📅 {film_year}\n"
                        f"🎭 Жанры: {genres_str}\n"
                        f"⭐️ Рейтинг Кинопоиск: {kp_rating}\n"
                        f"📊 Рейтинг IMDb: {imdb_rating}"
                    )
                    
                    # Добавляем информацию о сезонах для сериала или длительность для фильма
                    if film_type == 'TV_SERIES':
                        try:
                            seasons_response = requests.get(
                                f'https://kinopoiskapiunofficial.tech/api/v2.2/films/{film_id}/seasons',
                                headers=headers
                            )
                            seasons_data = seasons_response.json()
                            if seasons_data.get('items'):
                                seasons_count = len(seasons_data['items'])
                                message_text += f"\n📺 Сезонов: {seasons_count}"
                            else:
                                message_text += "\n📺 Сериал"
                        except Exception as e:
                            print(f"Error getting seasons info: {e}")
                            message_text += "\n📺 Сериал"
                    elif film_length:
                        message_text += f"\n⏱️ Длительность: {film_length} мин."
                    
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
                return
                
            bot.reply_to(message, "К сожалению, я не смог найти этот фильм. Попробуйте уточнить название.")
            
        except Exception as e:
            print(f"Error: {e}")
            bot.reply_to(message, "Произошла ошибка при поиске фильма. Попробуйте еще раз.")
