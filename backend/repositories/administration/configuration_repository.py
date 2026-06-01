from sqlmodel import Session

from models.administration.configuration import Configuration
from repositories.base_repository import BaseRepository


class ConfigurationRepository(BaseRepository[Configuration]):

    def __init__(self, session: Session):
        super().__init__(Configuration, session)
