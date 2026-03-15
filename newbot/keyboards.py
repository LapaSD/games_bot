import logging
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

logger = logging.getLogger(__name__)


class GameCallback(CallbackData, prefix="game"):
    id: int
    name: str
    release_year: int
    price: int


class ClearGamesCallback(CallbackData, prefix="clear"):
    action: str


def games_keyboard_markup(games_list: list[dict]):
    logger.info(f"Creating games keyboard. Games count: {len(games_list)}")

    builder = InlineKeyboardBuilder()

    for index, game in enumerate(games_list):

        try:
            builder.button(
                text=game["name"],
                callback_data=GameCallback(
                    id=index,
                    name=game["name"],
                    description=game.get("description", "Немає опису"),
                    release_year=int(
                        game.get("release_date", "0").split("-")[0]
                        if game.get("release_date")
                        else 0
                    )
                ).pack()
            )

        except Exception as e:
            logger.error(f"Error creating button for game: {game}. Error: {e}")

    builder.adjust(1)

    logger.info("Games keyboard successfully created")

    return builder.as_markup()