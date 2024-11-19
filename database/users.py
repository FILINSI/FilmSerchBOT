user_settings = {}
shown_films = {}  # Словарь для хранения показанных фильмов

def get_user_films_count(user_id):
    return user_settings.get(user_id, {}).get('films_count', 5)

def set_user_films_count(user_id, count):
    if user_id not in user_settings:
        user_settings[user_id] = {}
    user_settings[user_id]['films_count'] = count

def add_shown_film(user_id, genre_id, film_id):
    if user_id not in shown_films:
        shown_films[user_id] = {}
    if genre_id not in shown_films[user_id]:
        shown_films[user_id][genre_id] = set()
    shown_films[user_id][genre_id].add(film_id)

def clear_shown_films(user_id, genre_id):
    if user_id in shown_films and genre_id in shown_films[user_id]:
        shown_films[user_id][genre_id].clear()

def is_film_shown(user_id, genre_id, film_id):
    return (user_id in shown_films and 
            genre_id in shown_films[user_id] and 
            film_id in shown_films[user_id][genre_id])