from typing import Optional

from sqlmodel import Field, SQLModel


class SectionBase(SQLModel):
    code: str = Field(
        unique=True, max_length=10, description="Code unique de la section", nullable=False)
    libelle: str = Field(
        max_length=60, description="Libelle de la section", nullable=False)


class SectionCreateDTO(SectionBase):
    pass


class SectionUpdateDTO(SQLModel):
    code: Optional[str] = None
    libelle: Optional[str] = None


class SectionResponseDTO(SectionBase):
    id: int
