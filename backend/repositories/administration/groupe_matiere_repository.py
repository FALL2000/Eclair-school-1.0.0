from sqlmodel import Session

from models.administration.groupe_matiere import GroupeMatiere
from repositories.base_repository import BaseRepository


class GroupeMatiereRepository(BaseRepository[GroupeMatiere]):

    def __init__(self, session: Session):
        super().__init__(GroupeMatiere, session)
