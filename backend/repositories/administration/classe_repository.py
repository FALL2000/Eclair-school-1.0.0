from sqlmodel import Session

from models.administration.classe import Classe
from repositories.base_repository import BaseRepository


class ClasseRepository(BaseRepository[Classe]):

    def __init__(self, session: Session):
        super().__init__(Classe, session)
