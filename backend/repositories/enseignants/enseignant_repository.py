from sqlmodel import Session, select, func

from models.enseignants.enseignant import Enseignant
from repositories.base_repository import BaseRepository


class EnseignantRepository(BaseRepository[Enseignant]):

    def __init__(self, session: Session):
        super().__init__(Enseignant, session)

    def count_all(self) -> int:
        statement = select(func.count()).select_from(Enseignant)
        return self.session.exec(statement).one()
