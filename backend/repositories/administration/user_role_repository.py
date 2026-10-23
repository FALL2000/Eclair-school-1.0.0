from sqlmodel import Session

from models.administration.user_role import UserRole
from repositories.base_repository import BaseRepository


class UserRoleRepository(BaseRepository[UserRole]):

    def __init__(self, session: Session):
        super().__init__(UserRole, session)
