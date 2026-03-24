from typing import Optional

from sqlmodel import Field, SQLModel


class ClasseBase(SQLModel):
    code: str = Field(
        unique=True, max_length=10, description="Code unique de la classe", nullable=False)
    libelle: str = Field(
        max_length=60, description="Libelle de la classe", nullable=False)


class ClasseCreateDTO(ClasseBase):
    pass


class ClasseUpdateDTO(SQLModel):
    code: Optional[str] = None
    libelle: Optional[str] = None


class ClasseResponseDTO(ClasseBase):
    id: int
