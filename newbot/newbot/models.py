from dataclasses import dataclass
import logging 

logger = logging.getLogger(__name__)


@dataclass
class Game:
    name: str
    genre: str
    release_date: int