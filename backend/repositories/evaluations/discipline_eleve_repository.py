from sqlmodel import Session

from models.evaluations.discipline_eleve import DisciplineEleve
from repositories.base_repository import BaseRepository


class DisciplineEleveRepository(BaseRepository[DisciplineEleve]):

    def __init__(self, session: Session):
        super().__init__(DisciplineEleve, session)
