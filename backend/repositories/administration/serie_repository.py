from sqlmodel import Session

from models.administration.serie import Serie
from repositories.base_repository import BaseRepository


class SerieRepository(BaseRepository[Serie]):

    def __init__(self, session: Session):
        super().__init__(Serie, session)
