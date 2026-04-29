from typing import List, Optional

from sqlmodel import Field, SQLModel

from schemas.administration.classe_dto import ClasseResponseDTO


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
    montant_inscription: Optional[float] = None


class NiveauResponseDTO(NiveauBase):
    id: int


class NiveauReadWithClasse(NiveauResponseDTO):
    classes: List[ClasseResponseDTO]
