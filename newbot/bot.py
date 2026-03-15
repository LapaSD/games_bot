import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from state_machine import GameForm
from config import TOKEN
from commands import (
    ADD_GAME_COMMAND,
    DELETE_GAME_COMMAND,
    SORT_PRICE_BOT_COMMAND,
    SORT_PRICE_COMMAND,
    START_BOT_COMMAND,
    ADD_GAME_BOT_COMMAND,
    DELETE_GAME_BOT_COMMAND,
    START_COMMAND,
    GAME_LIST_COMMAND,
    GAME_LIST_BOT_COMMAND,
    CLEAR_GAMES_COMMAND,
    CLEAR_GAMES_BOT_COMMAND
)

from data import read_user_data, add_game, delete_game, clear_games
from models import Game
from keyboards import GameCallback, ClearGamesCallback


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("bot_logger.log", mode="a", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

dp = Dispatcher()


@dp.message(START_COMMAND)
async def command_start_func(message: Message, state: FSMContext):
    await state.clear()
    """Привітання користувача при старті бота"""

    await message.answer(
        f"👋 Привіт, {message.from_user.first_name}!\n"
        f"Я бот для збереження списку ігор."
    )


@dp.message(ADD_GAME_COMMAND)
async def add_game_start(message: Message, state: FSMContext):

    """Початок процесу додавання гри"""

    await state.clear()

    await message.answer("Введіть назву гри:")

    await state.set_state(GameForm.name)


@dp.message(StateFilter(GameForm.name))
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введіть жанр гри:")
    await state.set_state(GameForm.genre)


@dp.message(StateFilter(GameForm.genre))
async def process_genre(message: Message, state: FSMContext):
    await state.update_data(genre=message.text)
    await message.answer("Введіть рік випуску гри:")
    await state.set_state(GameForm.release_year)


@dp.message(StateFilter(GameForm.release_year))
async def process_release_year(message: Message, state: FSMContext):

    await state.update_data(release_year=message.text)

    await message.answer("Введіть ціну гри:")

    await state.set_state(GameForm.price)


@dp.message(StateFilter(GameForm.price))
async def process_price(message: Message, state: FSMContext):

    """Завершення процесу додавання гри та збереження даних"""

    await state.update_data(price=message.text)

    data = await state.get_data()

    game = Game(
        name=data["name"],
        genre=data["genre"],
        release_date=f"{data['release_year']}-01-01",
        price=data["price"]
    )

    add_game(game)
    await state.clear()
    await message.answer("✅ Гру успішно додано!")


@dp.message(SORT_PRICE_COMMAND)
async def sort_games_by_price(message: Message, state: FSMContext):

    await state.clear()

    games = read_user_data()

    if not games:
        await message.answer("❌ Список ігор порожній.")
        return

    try:
        sorted_games = sorted(
            games,
            key=lambda game: float(game.get("price", 0))
        )
    except ValueError:
        await message.answer("❌ Помилка у форматі ціни.")
        return

    response = "💰 Ігри від найдешевшої до найдорожчої:\n\n"

    for game in sorted_games:

        name = game.get("name", "Unknown")
        genre = game.get("genre", "Unknown")
        release_date = game.get("release_date", "Unknown")
        price = game.get("price", "Unknown")

        year = release_date.split("-")[0]

        response += (
            f"<b>{name}</b>\n"
            f"Жанр: {genre}\n"
            f"Рік: {year}\n"
            f"Ціна: {price}\n\n"
        )

    await message.answer(response)


@dp.message(GAME_LIST_COMMAND)
async def game_list_handler(message: Message, state: FSMContext):

    """Виведення списку ігор"""

    await state.clear()

    games = read_user_data()

    if not games:
        await message.answer("Список ігор порожній.")
        return

    response = "<b>🎮 Список ігор:</b>\n\n"

    for game in games:

        name = game.get("name", "Unknown")
        genre = game.get("genre", "Unknown")
        release_date = game.get("release_date", "Unknown")
        price = game.get("price", "Unknown")

        year = release_date.split("-")[0] if release_date != "Unknown" else "Unknown"

        response += (
            f"<b>{name}</b>\n"
            f"Жанр: {genre}\n"
            f"Рік: {year}\n"
            f"Ціна: {price}\n\n"
        )

    await message.answer(response)


@dp.message(DELETE_GAME_COMMAND)
async def command_delete_game_handler(message: Message, state: FSMContext):

    """Видалення гри за назвою"""

    await state.clear()

    try:
        _, game_name = message.text.split(maxsplit=1)
    except ValueError:
        await message.answer("Формат: /delete_game Назва")
        return

    success = delete_game(game_name)

    if success:
        await message.answer("🗑 Гру видалено!")
    else:
        await message.answer("❌ Гру не знайдено.")


@dp.message(CLEAR_GAMES_COMMAND)
async def clear_games_command(message: Message):

    """Початок процесу очищення списку ігор"""

    games = read_user_data()

    if not games:
        await message.answer("❌ Список ігор порожній.")
        return

    await message.answer(
        "⚠️ Ви впевнені що хочете стерти всі ігри?",
        reply_markup=clear_games_keyboard()
    )


def clear_games_keyboard():

    builder = InlineKeyboardBuilder()

    builder.button(
        text="✅ Так",
        callback_data=ClearGamesCallback(action="yes").pack()
    )

    builder.button(
        text="❌ Ні",
        callback_data=ClearGamesCallback(action="no").pack()
    )

    builder.adjust(2)

    return builder.as_markup()


@dp.callback_query(ClearGamesCallback.filter())
async def clear_games_callback(callback: CallbackQuery, callback_data: ClearGamesCallback):

    if callback_data.action == "yes":

        success = clear_games()

        if success:
            await callback.message.answer("🗑 Усі ігри видалені.")
        else:
            await callback.message.answer("❌ Помилка очищення.")

    else:
        await callback.message.answer("❎ Очищення скасовано.")

    await callback.answer()


@dp.message()
async def echo_handler(message: Message):

    await message.answer(
        "Я розумію тільки команди:\n"
        "/start\n"
        "/game_list\n"
        "/add_game\n"
        "/delete_game\n"
        "/clear_games"
    )


async def main():

    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    await bot.set_my_commands(
        [
            START_BOT_COMMAND,
            ADD_GAME_BOT_COMMAND,
            DELETE_GAME_BOT_COMMAND,
            GAME_LIST_BOT_COMMAND,
            SORT_PRICE_BOT_COMMAND,
            CLEAR_GAMES_BOT_COMMAND,
        ]
    )

    await dp.start_polling(bot)


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        logger.info("Bot stopped manually")