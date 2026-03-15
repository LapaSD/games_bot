import json
import os
import logging
from models import Game

logger = logging.getLogger(__name__)

FILE_PATH = "games_data.json"


def read_all_data(file_path: str = FILE_PATH) -> list:
    """
    Зчитує всі ігри з JSON файлу.
    Якщо файл не існує — повертає порожній список.
    """

    logger.info("Reading all games from file")

    if not os.path.exists(file_path):
        logger.warning("Data file not found, returning empty list")
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

            if isinstance(data, list):
                return data

            return []

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return []

    except Exception as e:
        logger.error(f"Unexpected error while reading file: {e}")
        return []


def read_user_data(file_path: str = FILE_PATH) -> list:
    """
    Повертає весь список ігор.
    """

    games = read_all_data(file_path)

    logger.info(f"Total games in database: {len(games)}")

    return games


def add_game(game: Game, file_path: str = FILE_PATH) -> None:
    """
    Додає нову гру до загального списку.
    """

    logger.info(f"Adding game: {game.name}")

    data = read_all_data(file_path)

    game_data = {
    "name": game.name,
    "genre": game.genre,
    "release_date": game.release_date,
    "price": game.price
}

    data.append(game_data)

    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        logger.info(f"Game '{game.name}' successfully added")

    except Exception as e:
        logger.error(f"Error writing to file: {e}")


def delete_game(game_name: str, file_path: str = FILE_PATH) -> bool:
    """
    Видаляє гру зі списку.
    """

    logger.info(f"Attempting to delete game '{game_name}'")

    data = read_all_data(file_path)

    new_games = [
        g for g in data
        if g.get("name", "").lower() != game_name.lower()
    ]

    if len(data) == len(new_games):
        logger.warning(f"Game '{game_name}' not found")
        return False

    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(new_games, file, indent=4, ensure_ascii=False)

        logger.info(f"Game '{game_name}' successfully deleted")
        return True

    except Exception as e:
        logger.error(f"Error deleting game: {e}")
        return False


def clear_games(file_path: str = FILE_PATH) -> bool:
    """
    Видаляє всі ігри.
    """

    logger.info("Clearing all games")

    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump([], file, indent=4, ensure_ascii=False)

        logger.info("All games cleared")
        return True

    except Exception as e:
        logger.error(f"Error clearing games: {e}")
        return False