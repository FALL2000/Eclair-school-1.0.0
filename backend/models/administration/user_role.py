from typing import Optional, TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

from models.administration.role import Role

if TYPE_CHECKING:
    from models.administration.user import User


class UserRole(SQLModel, table=True):
    __tablename__ = "user_role"

    __table_args__ = (
        UniqueConstraint("id_user", "id_role", name="unique_role_user"),
    )

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id du role lié à un utilisateur"
    )
    id_user: int = Field(
        sa_column=Column(Integer, ForeignKey("user.id", ondelete="CASCADE")),
        description="Id de l'utilisateur associé",
    )
    id_role: int = Field(
        sa_column=Column(Integer, ForeignKey("role.id", ondelete="CASCADE")),
        description="Id du role associé",
    )

    user: "User" = Relationship(back_populates="user_roles")
    role: "Role" = Relationship(back_populates="roles_user")
