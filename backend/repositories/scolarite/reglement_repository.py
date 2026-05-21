from sqlmodel import Session, select, func

from models.scolarite.reglement import Reglement
from repositories.base_repository import BaseRepository


class ReglementRepository(BaseRepository[Reglement]):

    def __init__(self, session: Session):
        super().__init__(Reglement, session)

    def find_all_ordered_desc(self, limit: int | None = None, offset: int | None = None) -> list[Reglement]:
        statement = select(Reglement).order_by(Reglement.date_reglement.desc())
        if offset is not None:
            statement = statement.offset(offset)
        if limit is not None:
            statement = statement.limit(limit)
        return self.session.exec(statement).all()

    def count_all(self) -> int:
        statement = select(func.count()).select_from(Reglement)
        return self.session.exec(statement).one()
