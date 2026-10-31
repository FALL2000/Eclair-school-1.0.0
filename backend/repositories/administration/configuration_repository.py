from sqlmodel import Session

from models.administration.configuration import Configuration
from repositories.base_repository import BaseRepository


class ConfigurationRepository(BaseRepository[Configuration]):

    def __init__(self, session: Session):
        super().__init__(Configuration, session)

    def is_discipline_geree(self) -> bool:
        """La discipline est geree sauf si la configuration la desactive (pas de configuration : geree)"""
        configurations = self.findAll()
        return len(configurations) == 0 or configurations[0].is_discipline_manage
