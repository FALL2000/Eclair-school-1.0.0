from sqlmodel import Session, select

from models.administration.permission import Permission
from models.administration.role import Role
from models.administration.role_permission import RolePermission
from models.administration.user_role import UserRole
from repositories.base_repository import BaseRepository


class PermissionRepository(BaseRepository[Permission]):

    def __init__(self, session: Session):
        super().__init__(Permission, session)

    def find_roles_user(self, id_user: int) -> list[Role]:
        """Rôles attribués à un utilisateur"""
        statement = (
            select(Role)
            .join(UserRole, UserRole.id_role == Role.id)
            .where(UserRole.id_user == id_user)
        )
        return self.session.exec(statement).all()

    def find_codes_user(self, id_user: int) -> set[str]:
        """Codes des permissions de l'utilisateur (union des permissions de tous ses rôles)"""
        statement = (
            select(Permission.code)
            .join(RolePermission, RolePermission.id_permission == Permission.id)
            .join(UserRole, UserRole.id_role == RolePermission.id_role)
            .where(UserRole.id_user == id_user)
            .distinct()
        )
        return set(self.session.exec(statement).all())

    def find_permissions_role(self, id_role: int) -> list[Permission]:
        statement = (
            select(Permission)
            .join(RolePermission, RolePermission.id_permission == Permission.id)
            .where(RolePermission.id_role == id_role)
            .order_by(Permission.domaine, Permission.module, Permission.action)
        )
        return self.session.exec(statement).all()

    def find_all_ordered(self) -> list[Permission]:
        statement = select(Permission).order_by(Permission.domaine, Permission.module, Permission.action)
        return self.session.exec(statement).all()
