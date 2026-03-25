from typing import Optional

from sqlmodel import Field, SQLModel


class TrimestreBase(SQLModel):
    code: str = Field(
        unique=True,
        max_length=10,
        description="Code unique du trimestre",
        nullable=False,
    )
    libelle: str = Field(
        max_length=60,
        description="Libellé du trimestre",
        nullable=False,
    )


class TrimestreCreateDTO(TrimestreBase):
    pass


class TrimestreUpdateDTO(SQLModel):
    code: Optional[str] = None
    libelle: Optional[str] = None


class TrimestreResponseDTO(TrimestreBase):
    id: int

