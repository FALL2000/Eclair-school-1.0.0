from sqlmodel import Session

from models.administration.annee import Annee
from repositories.base_repository import BaseRepository


class AnneeRepository(BaseRepository[Annee]):

    def __init__(self, session: Session):
        super().__init__(Annee, session)
