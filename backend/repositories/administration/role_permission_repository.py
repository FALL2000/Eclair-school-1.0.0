from sqlmodel import Session

from models.administration.role_permission import RolePermission
from repositories.base_repository import BaseRepository


class RolePermissionRepository(BaseRepository[RolePermission]):

    def __init__(self, session: Session):
        super().__init__(RolePermission, session)
