from sqlmodel import Session

from models.administration.niveau import Niveau
from repositories.base_repository import BaseRepository


class NiveauRepository(BaseRepository[Niveau]):

    def __init__(self, session: Session):
        super().__init__(Niveau, session)
