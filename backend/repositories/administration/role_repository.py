from sqlmodel import Session

from models.administration.role import Role
from repositories.base_repository import BaseRepository


class RoleRepository(BaseRepository[Role]):

    def __init__(self, session: Session):
        super().__init__(Role, session)
