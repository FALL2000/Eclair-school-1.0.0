from typing import Optional

from sqlmodel import Field, SQLModel


class MatiereEvalueBase(SQLModel):
    code: str = Field(
        unique=True,
        max_length=10,
        description="Code unique de la matière évaluée",
        nullable=False,
    )
    libelle: str = Field(
        max_length=60,
        description="Libellé de la matière évaluée",
        nullable=False,
    )
    type: str = Field(
        max_length=30,
        description="Type de matière évaluée (Ecrite, Orale, Pratique)",
        nullable=False,
    )
    coefficient: Optional[int] = Field(
        default=None,
        description="Coefficient appliqué à la note",
        nullable=True,
    )


class MatiereEvalueCreateDTO(MatiereEvalueBase):
    pass


class MatiereEvalueUpdateDTO(SQLModel):
    code: Optional[str] = None
    libelle: Optional[str] = None
    type: Optional[str] = None
    coefficient: Optional[int] = None


class MatiereEvalueResponseDTO(MatiereEvalueBase):
    id: int
