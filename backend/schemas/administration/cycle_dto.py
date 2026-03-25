from typing import Optional

from sqlmodel import Field, SQLModel


class CycleBase(SQLModel):
    code: str = Field(
        unique=True, max_length=10, description="Code unique du cycle", nullable=False)
    libelle: str = Field(
        max_length=60, description="Libelle du cycle", nullable=False)


class CycleCreateDTO(CycleBase):
    pass


class CycleUpdateDTO(SQLModel):
    code: Optional[str] = None
    libelle: Optional[str] = None


class CycleResponseDTO(CycleBase):
    id: int
