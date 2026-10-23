from typing import Optional, TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

if TYPE_CHECKING:
    from models.administration.permission import Permission
    from models.administration.role import Role


class RolePermission(SQLModel, table=True):
    """Permissions attribuées à un rôle (un rôle peut avoir plusieurs permissions)"""
    __tablename__ = "role_permission"

    __table_args__ = (
        UniqueConstraint("id_role", "id_permission", name="unique_role_permission"),
    )

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id de la permission attribuée au rôle"
    )
    id_role: int = Field(
        sa_column=Column(Integer, ForeignKey("role.id", ondelete="CASCADE"), nullable=False),
        description="Id du rôle",
    )
    id_permission: int = Field(
        sa_column=Column(Integer, ForeignKey("permission.id", ondelete="CASCADE"), nullable=False),
        description="Id de la permission",
    )

    role: "Role" = Relationship(back_populates="permissions_role")
    permission: "Permission" = Relationship(back_populates="roles_permission")
