from typing import Optional

from sqlmodel import Field, SQLModel


class SerieBase(SQLModel):
    code: str = Field(
        unique=True, max_length=10, description="Code unique de la serie", nullable=False)
    libelle: str = Field(
        max_length=60, description="Libelle de la serie", nullable=False)


class SerieCreateDTO(SerieBase):
    pass


class SerieUpdateDTO(SQLModel):
    code: Optional[str] = None
    libelle: Optional[str] = None


class SerieResponseDTO(SerieBase):
    id: int
