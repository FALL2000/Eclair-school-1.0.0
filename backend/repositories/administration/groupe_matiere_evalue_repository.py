from sqlmodel import Session

from models.administration.groupe_matiere_evalue import GroupeMatiereEvalue
from repositories.base_repository import BaseRepository


class GroupeMatiereEvalueRepository(BaseRepository[GroupeMatiereEvalue]):

    def __init__(self, session: Session):
        super().__init__(GroupeMatiereEvalue, session)
