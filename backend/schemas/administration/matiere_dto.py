from typing import Optional

from sqlmodel import Field, SQLModel


class MatiereBase(SQLModel):
    code: str = Field(
        unique=True,
        max_length=10,
        description="Code unique de la matière",
        nullable=False,
    )
    libelle: str = Field(
        max_length=60,
        description="Libellé de la matière",
        nullable=False,
    )


class MatiereCreateDTO(MatiereBase):
    pass


class MatiereUpdateDTO(SQLModel):
    code: Optional[str] = None
    libelle: Optional[str] = None


class MatiereResponseDTO(MatiereBase):
    id: int

