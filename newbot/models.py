from dataclasses import dataclass
import logging 

logger = logging.getLogger(__name__)


@dataclass
class Game:
    def __init__(self, name, genre, release_date, price):
        self.name = name
        self.genre = genre
        self.release_date = release_date
        self.price = price