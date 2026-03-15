from aiogram.filters import Command
from aiogram.types.bot_command import BotCommand
import logging 

logger = logging.getLogger(__name__)


GAME_LIST_COMMAND = Command("game_list")
START_COMMAND = Command('start')
ADD_GAME_COMMAND = Command('add_game')
DELETE_GAME_COMMAND = Command('delete_game')
CLEAR_GAMES_COMMAND = Command("clear_games")
SORT_PRICE_COMMAND = Command("sort_price")


logger.info("Command filters initialized")


START_BOT_COMMAND = BotCommand(command='start', description="Почати розмову")
ADD_GAME_BOT_COMMAND = BotCommand(command='add_game', description="Додати гру до списку")
DELETE_GAME_BOT_COMMAND = BotCommand(command='delete_game', description="Видалити гру зі списку")
GAME_LIST_BOT_COMMAND = BotCommand(command="game_list",description="Показати список ігор з жанром та роком")
CLEAR_GAMES_BOT_COMMAND = BotCommand(command="clear_games",description="Очистити список ігор")
SORT_PRICE_BOT_COMMAND = BotCommand(    command="sort_price",    description="Сортувати ігри за ціною")


logger.info("Bot commands initialized")