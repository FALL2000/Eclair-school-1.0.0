from sqlmodel import Session

from models.administration.user import User
from repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):

    def __init__(self, session: Session):
        super().__init__(User, session)
