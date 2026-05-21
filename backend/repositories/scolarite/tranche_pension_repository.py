from sqlmodel import Session

from models.scolarite.tranche_pension import TranchePension
from repositories.base_repository import BaseRepository


class TranchePensionRepository(BaseRepository[TranchePension]):

    def __init__(self, session: Session):
        super().__init__(TranchePension, session)
