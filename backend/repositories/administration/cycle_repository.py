from sqlmodel import Session

from models.administration.cycle import Cycle
from repositories.base_repository import BaseRepository


class CycleRepository(BaseRepository[Cycle]):

    def __init__(self, session: Session):
        super().__init__(Cycle, session)
