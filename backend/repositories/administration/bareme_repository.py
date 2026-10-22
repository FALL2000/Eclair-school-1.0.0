from sqlmodel import Session

from models.administration.bareme import Bareme
from repositories.base_repository import BaseRepository


class BaremeRepository(BaseRepository[Bareme]):

    def __init__(self, session: Session):
        super().__init__(Bareme, session)
