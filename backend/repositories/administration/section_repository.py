from sqlmodel import Session

from models.administration.section import Section
from repositories.base_repository import BaseRepository


class SectionRepository(BaseRepository[Section]):

    def __init__(self, session: Session):
        super().__init__(Section, session)
