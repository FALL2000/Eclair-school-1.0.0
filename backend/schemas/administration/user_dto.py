from typing import Optional

from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    username: str = Field(
        unique=True,
        max_length=50,
        description="Nom d'utilisateur",
        nullable=False,
    )
    nom: Optional[str] = Field(
        default=None,
        max_length=60,
        description="Nom",
        nullable=True,
    )
    prenom: Optional[str] = Field(
        default=None,
        max_length=60,
        description="Prénom",
        nullable=True,
    )


class UserCreateDTO(UserBase):
    password: str = Field(
        min_length=6,
        max_length=128,
        description="Mot de passe en clair à hasher",
        nullable=False,
    )


class UserUpdateDTO(SQLModel):
    username: Optional[str] = None
    nom: Optional[str] = None
    prenom: Optional[str] = None


class UserResponseDTO(UserBase):
    id: int

