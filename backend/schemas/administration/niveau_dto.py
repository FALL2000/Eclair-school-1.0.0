from typing import Optional

from sqlmodel import Field, SQLModel


class NiveauBase(SQLModel):
    code: str = Field(
        unique=True, max_length=10, description="Code unique du niveau", nullable=False)
    libelle: str = Field(
        max_length=60, description="Libelle du niveau", nullable=False)
    montant_inscription: float = Field(
        description="Montant de l'inscription pour le niveau", nullable=False)


class NiveauCreateDTO(NiveauBase):
    pass


class NiveauUpdateDTO(SQLModel):
    code: Optional[str] = None
    libelle: Optional[str] = None


class NiveauResponseDTO(NiveauBase):
    id: int
