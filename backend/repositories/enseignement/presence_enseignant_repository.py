from sqlmodel import Session

from models.enseignement.presence_enseignant import PresenceEnseignant
from repositories.base_repository import BaseRepository


class PresenceEnseignantRepository(BaseRepository[PresenceEnseignant]):

    def __init__(self, session: Session):
        super().__init__(PresenceEnseignant, session)
