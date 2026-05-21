from sqlmodel import Session

from models.enseignement.enseignement import Enseignement
from repositories.base_repository import BaseRepository


class EnseignementRepository(BaseRepository[Enseignement]):

    def __init__(self, session: Session):
        super().__init__(Enseignement, session)
