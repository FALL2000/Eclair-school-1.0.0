from sqlmodel import Session

from models.administration.appreciation import Appreciation
from repositories.base_repository import BaseRepository


class AppreciationRepository(BaseRepository[Appreciation]):

    def __init__(self, session: Session):
        super().__init__(Appreciation, session)
