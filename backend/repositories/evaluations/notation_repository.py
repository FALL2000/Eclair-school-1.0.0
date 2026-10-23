from sqlmodel import Session

from models.evaluations.notation import Notation
from repositories.base_repository import BaseRepository


class NotationRepository(BaseRepository[Notation]):

    def __init__(self, session: Session):
        super().__init__(Notation, session)
