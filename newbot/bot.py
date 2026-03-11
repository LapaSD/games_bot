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
from aiogram.filters.callback_data import CallbackData

from state_machine import GameForm, GenreSearchForm
from config import TOKEN
from commands import (
    ADD_GAME_COMMAND,
    DELETE_GAME_COMMAND,
    START_BOT_COMMAND,
    ADD_GAME_BOT_COMMAND,
    DELETE_GAME_BOT_COMMAND,
    START_COMMAND,
    GAME_LIST_COMMAND,
    GAME_LIST_BOT_COMMAND,
    SEARCH_GENRE_COMMAND,
    SEARCH_GENRE_BOT_COMMAND,
    CLEAR_GAMES_COMMAND,
    CLEAR_GAMES_BOT_COMMAND
)
from data import read_user_data, add_game, delete_game, clear_games
from models import Game
from keyboards import games_keyboard_markup, GameCallback, ClearGamesCallback


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
    """
    Обробник команди /start.
    Очищає FSM стан користувача та надсилає привітальне повідомлення.
    """
    await state.clear()
    logger.info(f"User {message.from_user.id} used /start")
    await message.answer(
        f"👋 Привіт, {message.from_user.first_name}!\n"
        f"Я бот для збереження списку ігор, для зручності користування, є меню знизу.\n"
    )


@dp.message(SEARCH_GENRE_COMMAND)
async def search_genre_start(message: Message, state: FSMContext):
    """
    Початок пошуку ігор за жанром.
    Бот запитує у користувача жанр і переводить FSM у стан очікування введення жанру.
    """
    await state.clear()
    logger.info(f"User {message.from_user.id} started genre search")
    await message.answer("Введіть жанр для пошуку:")
    await state.set_state(GenreSearchForm.waiting_for_genre)


@dp.message(CLEAR_GAMES_COMMAND)
async def clear_games_command(message: Message):
    """
    Обробник команди /clear_games.
    Відправляє повідомлення з підтвердженням для очищення всіх ігор користувача.
    """
    logger.info(f"User {message.from_user.id} requested clear games")
    await message.answer(
        "⚠️ Ви впевнені що хочете стерти всі ігри?",
        reply_markup=clear_games_keyboard()
    )


def clear_games_keyboard():
    """
    Створює клавіатуру з кнопками "Так" та "Ні" для підтвердження очищення ігор.
    """
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
    """
    Обробляє натискання кнопок "Так/Ні" для очищення ігор користувача.
    """
    user_id = str(callback.from_user.id)
    if callback_data.action == "yes":
        logger.info(f"User {user_id} confirmed clearing games")
        success = clear_games(user_id)
        if success:
            await callback.message.answer("🗑 Усі ігри успішно видалені.")
        else:
            await callback.message.answer("❌ Помилка очищення ігор.")
    else:
        logger.info(f"User {user_id} canceled clearing games")
        await callback.message.answer("❎ Очищення скасовано.")
    await callback.answer()


@dp.callback_query(GameCallback.filter())
async def game_details(callback: CallbackQuery, callback_data: GameCallback):
    """
    Показує деталі гри при натисканні на кнопку.
    """
    logger.info(f"User {callback.from_user.id} opened game: {callback_data.name}")
    await callback.message.answer(f"🎮 Назва: {callback_data.name}")
    await callback.answer()


@dp.message(ADD_GAME_COMMAND)
async def add_game_start(message: Message, state: FSMContext):
    """
    Початок додавання гри. Запитує назву гри і переводить FSM у стан введення назви.
    """
    await state.clear()
    logger.info(f"User {message.from_user.id} started adding a game")
    await message.answer("Введіть назву гри:")
    await state.set_state(GameForm.name)


@dp.message(StateFilter(GameForm.name))
async def process_name(message: Message, state: FSMContext):
    """
    Обробка введення назви гри.
    """
    logger.info(f"Game name received: {message.text}")
    await state.update_data(name=message.text)
    await message.answer("Введіть жанр гри:")
    await state.set_state(GameForm.genre)


@dp.message(StateFilter(GameForm.genre))
async def process_genre(message: Message, state: FSMContext):
    """
    Обробка введення жанру гри.
    """
    logger.info(f"Game genre received: {message.text}")
    await state.update_data(genre=message.text)
    await message.answer("Введіть рік випуску гри:")
    await state.set_state(GameForm.release_year)


@dp.message(StateFilter(GameForm.release_year))
async def process_release_year(message: Message, state: FSMContext):
    """
    Завершення додавання гри. Зберігає гру у JSON.
    """
    logger.info(f"Release year received: {message.text}")
    await state.update_data(release_year=message.text)
    data = await state.get_data()
    user_id = str(message.from_user.id)
    game = Game(
        name=data["name"],
        genre=data["genre"],
        release_date=f"{data['release_year']}-01-01"
    )
    add_game(user_id, game)
    logger.info(f"Game added for user {user_id}: {data['name']}")
    await state.clear()
    await message.answer("✅ Гру успішно додано!")


@dp.message(GenreSearchForm.waiting_for_genre)
async def process_genre_search(message: Message, state: FSMContext):
    """
    Пошук ігор за жанром. Показує знайдені ігри користувачу.
    """
    user_id = str(message.from_user.id)
    genre_input = message.text.lower()
    logger.info(f"User {user_id} searching games by genre: {genre_input}")
    games = read_user_data(user_id)
    if not games:
        logger.info(f"No games found for user {user_id}")
        await message.answer("У вас поки немає ігор.")
        await state.clear()
        return
    found_games = [game for game in games if game.get("genre", "").lower() == genre_input]
    if not found_games:
        logger.info(f"No games found with genre {genre_input}")
        await message.answer("Ігри з таким жанром не знайдено.")
        await state.clear()
        return
    response = "<b>🎮 Знайдені ігри:</b>\n\n"
    for game in found_games:
        name = game.get("name", "Unknown")
        release_date = game.get("release_date", "Unknown")
        year = release_date.split("-")[0] if release_date != "Unknown" else "Unknown"
        response += f"<b>{name}</b>\nЖанр: {game.get('genre')}\nРік: {year}\n\n"
    logger.info(f"Found {len(found_games)} games for genre {genre_input}")
    await message.answer(response)
    await state.clear()


@dp.message(DELETE_GAME_COMMAND)
async def command_delete_game_handler(message: Message, state: FSMContext) -> None:
    """
    Видалення гри за назвою (/delete_game Назва).
    """
    await state.clear()
    user_id = str(message.from_user.id)
    try:
        _, game_name = message.text.split(maxsplit=1)
    except ValueError:
        await message.answer("Формат: /delete_game Назва")
        return
    logger.info(f"User {user_id} trying to delete game: {game_name}")
    success = delete_game(user_id, game_name)
    if success:
        logger.info(f"Game deleted: {game_name}")
        await message.answer("🗑 Гру видалено!")
    else:
        logger.warning(f"Game not found for deletion: {game_name}")
        await message.answer("❌ Гру не знайдено.")


@dp.message(GAME_LIST_COMMAND)
async def game_list_handler(message: Message, state: FSMContext):
    """
    Відображає повний список ігор користувача.
    """
    await state.clear()
    user_id = str(message.from_user.id)
    logger.info(f"User {user_id} requested full game list")
    games = read_user_data(user_id)
    if not games:
        await message.answer("У вас поки немає ігор у списку.")
        return
    response = "<b>🎮 Ваш список ігор:</b>\n\n"
    for game in games:
        name = game.get("name", "Unknown")
        genre = game.get("genre", "Unknown")
        release_date = game.get("release_date", "Unknown")
        year = release_date.split("-")[0] if release_date != "Unknown" else "Unknown"
        response += f"<b>{name}</b>\nЖанр: {genre}\nРік: {year}\n\n"
    await message.answer(response)


@dp.message()
async def echo_handler(message: Message) -> None:
    """
    Обробляє невідомі команди та повідомлення.
    """
    logger.warning(f"Unknown command from user {message.from_user.id}: {message.text}")
    await message.answer(
        "Я розумію тільки команди:\n"
        "/start\n"
        "/games\n"
        "/game_list\n"
        "/add_game\n"
        "/delete_game\n"
        "/clear_games"
    )


async def main() -> None:
    """
    Головна функція запуску бота.
    Реєструє команди та запускає polling.
    """
    logger.info("Bot is starting...")
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
            SEARCH_GENRE_BOT_COMMAND,
            CLEAR_GAMES_BOT_COMMAND,
        ]
    )
    logger.info("Commands registered successfully")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped manually")