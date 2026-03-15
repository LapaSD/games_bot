from aiogram.fsm.state import State, StatesGroup
import logging 


logger = logging.getLogger(__name__)


class GameForm(StatesGroup):
    name = State()  
    genre = State()
    release_year = State()


class GenreSearchForm(StatesGroup):
    waiting_for_genre = State()
  