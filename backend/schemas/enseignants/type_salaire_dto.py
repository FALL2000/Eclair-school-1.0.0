from typing import Optional

from sqlmodel import Field, SQLModel


class TypeSalaireBase(SQLModel):
    code: str = Field(
        unique=True, max_length=10, description="Code unique du type de salaire", nullable=False)
    libelle: str = Field(
        max_length=60, description="Libelle du type de salaire(Mensuel, Horaire)", nullable=False)


class TypeSalaireCreateDTO(TypeSalaireBase):
    pass


class TypeSalaireUpdateDTO(SQLModel):
    code: Optional[str] = None
    libelle: Optional[str] = None


class TypeSalaireResponseDTO(TypeSalaireBase):
    id: int
