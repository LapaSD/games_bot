from aiogram.filters import Command
from aiogram.types.bot_command import BotCommand
import logging 

logger = logging.getLogger(__name__)


GAME_LIST_COMMAND = Command("game_list")
START_COMMAND = Command('start')
ADD_GAME_COMMAND = Command('add_game')
DELETE_GAME_COMMAND = Command('delete_game')
SEARCH_GENRE_COMMAND = Command("search_genre")
CLEAR_GAMES_COMMAND = Command("clear_games")


logger.info("Command filters initialized")


START_BOT_COMMAND = BotCommand(command='start', description="Почати розмову")
ADD_GAME_BOT_COMMAND = BotCommand(command='add_game', description="Додати гру до списку")
DELETE_GAME_BOT_COMMAND = BotCommand(command='delete_game', description="Видалити гру зі списку")
GAME_LIST_BOT_COMMAND = BotCommand(command="game_list",description="Показати список ігор з жанром та роком")
SEARCH_GENRE_BOT_COMMAND = BotCommand(command="search_genre",description="Пошук ігор за жанром")
CLEAR_GAMES_BOT_COMMAND = BotCommand(command="clear_games",description="Очистити список ігор")


logger.info("Bot commands initialized")