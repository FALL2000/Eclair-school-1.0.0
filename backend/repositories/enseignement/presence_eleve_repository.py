from sqlmodel import Session

from models.enseignement.presence_eleve import PresenceEleve
from repositories.base_repository import BaseRepository


class PresenceEleveRepository(BaseRepository[PresenceEleve]):

    def __init__(self, session: Session):
        super().__init__(PresenceEleve, session)
