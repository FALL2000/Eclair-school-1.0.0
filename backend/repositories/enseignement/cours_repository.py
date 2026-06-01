from sqlmodel import Session

from models.enseignement.cours import Cours
from repositories.base_repository import BaseRepository


class CoursRepository(BaseRepository[Cours]):

    def __init__(self, session: Session):
        super().__init__(Cours, session)
