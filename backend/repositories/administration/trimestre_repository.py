from sqlmodel import Session

from models.administration.trimestre import Trimestre
from repositories.base_repository import BaseRepository


class TrimestreRepository(BaseRepository[Trimestre]):

    def __init__(self, session: Session):
        super().__init__(Trimestre, session)
