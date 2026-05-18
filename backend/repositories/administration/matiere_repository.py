from sqlmodel import Session

from models.administration.matiere import Matiere
from repositories.base_repository import BaseRepository


class MatiereRepository(BaseRepository[Matiere]):

    def __init__(self, session: Session):
        super().__init__(Matiere, session)
