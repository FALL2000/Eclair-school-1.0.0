from sqlmodel import Session

from models.administration.matiere_evalue import MatiereEvalue
from repositories.base_repository import BaseRepository


class MatiereEvalueRepository(BaseRepository[MatiereEvalue]):

    def __init__(self, session: Session):
        super().__init__(MatiereEvalue, session)
