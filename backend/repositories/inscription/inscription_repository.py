from sqlmodel import Session

from models.inscription.inscription import Inscription
from repositories.base_repository import BaseRepository


class InscriptionRepository(BaseRepository[Inscription]):

    def __init__(self, session: Session):
        super().__init__(Inscription, session)
