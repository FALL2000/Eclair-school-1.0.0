from typing import Optional

from sqlmodel import Field, SQLModel


class AnneeBase(SQLModel):
    code: str = Field(
        unique=True, max_length=10, description="Code unique de l'annee", nullable=False)
    libelle: str = Field(
        max_length=60, description="Libelle de l'annee", nullable=False)


class AnneeCreateDTO(AnneeBase):
    pass


class AnneeUpdateDTO(SQLModel):
    code: Optional[str] = None
    libelle: Optional[str] = None


class AnneeResponseDTO(AnneeBase):
    id: int
    is_cloture: bool
