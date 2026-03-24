from typing import Optional
from sqlmodel import Field, SQLModel


class PermissionBase(SQLModel):
    element_name: str = Field(
        max_length=100,
        description="Nom de l'élément (classe qui gere une fonctionnalites ex: eleve, matiere, enseignant etc..)",
        nullable=False,
    )
    permission_value: str = Field(
        max_length=50,
        description="Valeur de permission (CREATE, VIEW, UPDATE, DELETE)",
        nullable=False,
    )


class PermissionCreateDTO(PermissionBase):
    pass


class PermissionUpdateDTO(SQLModel):
    element_name: Optional[str] = None
    permission_value: Optional[str] = None


class PermissionResponseDTO(PermissionBase):
    id: int
