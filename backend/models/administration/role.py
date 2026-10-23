from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship

from schemas.administration.role_dto import RoleBase

if TYPE_CHECKING:
    from models.administration.role_permission import RolePermission
    from models.administration.user_role import UserRole


class Role(RoleBase, table=True):
    __tablename__ = "role"

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id du rôle"
    )
    is_systeme: bool = Field(
        default=False,
        nullable=False,
        sa_column_kwargs={"server_default": "0"},
        description="Rôle de base du système (SUPER ADMIN, ADMIN) : ni renommable ni supprimable",
    )

    roles_user: list["UserRole"] = Relationship(back_populates="role",
                                                sa_relationship_kwargs={"cascade": "all, delete"})
    permissions_role: list["RolePermission"] = Relationship(
        back_populates="role", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
