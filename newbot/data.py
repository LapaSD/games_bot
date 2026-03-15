from functools import wraps
import json
import os
import logging
from models import Game

logger = logging.getLogger(__name__)

FILE_PATH = "games_data.json"


def read_all_data(file_path: str = FILE_PATH) -> dict:
    """
    Зчитує всі дані з JSON файлу.

    Якщо файл не існує або містить некоректний JSON,
    повертається порожній словник.
    """

    logger.info("Reading all data from file")

    if not os.path.exists(file_path):
        logger.warning("Data file not found, returning empty dictionary")
        return {}

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            logger.info("Data successfully loaded")
            return data

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return {}

    except Exception as e:
        logger.error(f"Unexpected error while reading file: {e}")
        return {}


def async_log_function_call(func):
    """Декоратор для асинхронних функцій"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger = logging.getLogger(__name__)
        msg = f"Відбувся виклик функції '{func.__name__}'"
        logger.info(msg=msg)
        return await func(*args, **kwargs)
    return wrapper


def sync_log_function_call(func):
    """Декоратор для звичайних (синхронних) функцій"""
    @wraps(func)
    def wrapper(*args, **kwargs): # Звичайний def, без async!
        logger = logging.getLogger(__name__)
        logger.info(f"Відбувся виклик функції '{func.__name__}'")
        return func(*args, **kwargs) # Без await!
    return wrapper


def read_user_data(user_id: str, file_path: str = FILE_PATH) -> list:
    """
    Повертає список ігор конкретного користувача.
    """

    if not user_id:
        logger.warning("read_user_data called without user_id")
        return []

    logger.info(f"Reading games for user {user_id}")

    data = read_all_data(file_path)
    user_games = data.get(user_id, [])

    logger.info(f"User {user_id} has {len(user_games)} games")

    return user_games


def add_game(user_id: str, game: Game, file_path: str = FILE_PATH) -> None:
    """
    Додає нову гру до списку користувача.
    """

    logger.info(f"Adding game for user {user_id}: {game.name}")

    data = read_all_data(file_path)

    if user_id not in data:
        logger.info(f"User {user_id} not found in database. Creating new entry.")
        data[user_id] = []

    game_data = {
        "name": game.name,
        "genre": game.genre,
        "release_date": game.release_date,
    }

    data[user_id].append(game_data)

    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        logger.info(f"Game '{game.name}' successfully added for user {user_id}")

    except Exception as e:
        logger.error(f"Error writing to file: {e}")


def delete_game(user_id: str, game_name: str, file_path: str = FILE_PATH) -> bool:
    """
    Видаляє гру зі списку користувача.
    Повертає True, якщо гра була успішно видалена.
    """

    logger.info(f"Attempting to delete game '{game_name}' for user {user_id}")

    data = read_all_data(file_path)

    if user_id not in data:
        logger.warning(f"User {user_id} not found in database")
        return False

    games = data[user_id]

    new_games = [
        g for g in games
        if g.get("name", "").lower() != game_name.lower()
    ]

    if len(games) == len(new_games):
        logger.warning(f"Game '{game_name}' not found for user {user_id}")
        return False

    data[user_id] = new_games

    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        logger.info(f"Game '{game_name}' successfully deleted for user {user_id}")
        return True

    except Exception as e:
        logger.error(f"Error writing to file during deletion: {e}")
        return False


def clear_games(user_id: str, file_path: str = FILE_PATH) -> bool:
    """
    Видаляє всі ігри користувача.
    Якщо користувача ще немає у файлі —
    створюється порожній запис.
    """

    logger.info(f"Clearing all games for user {user_id}")

    data = read_all_data(file_path)

    data[user_id] = []

    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        logger.info(f"All games cleared for user {user_id}")
        return True

    except Exception as e:
        logger.error(f"Error clearing games: {e}")
        return False