from sqlmodel import Session

from models.eleve.eleve import Eleve
from repositories.base_repository import BaseRepository


class EleveRepository(BaseRepository[Eleve]):

    def __init__(self, session: Session):
        super().__init__(Eleve, session)
