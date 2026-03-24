from datetime import date
from typing import Optional

from sqlmodel import Field, SQLModel


class EvaluationBase(SQLModel):
    code: str = Field(
        unique=True,
        max_length=10,
        description="Code unique de l'évaluation",
        nullable=False,
    )
    libelle: str = Field(
        max_length=60,
        description="Libellé de l'évaluation",
        nullable=False,
    )
    date_deb: date = Field(
        description="Date de début de l'évaluation",
        nullable=False,
    )
    date_fin: date = Field(
        description="Date de fin de l'évaluation",
        nullable=False,
    )


class EvaluationCreateDTO(EvaluationBase):
    pass


class EvaluationUpdateDTO(SQLModel):
    code: Optional[str] = None
    libelle: Optional[str] = None
    date_deb: Optional[date] = None
    date_fin: Optional[date] = None


class EvaluationResponseDTO(EvaluationBase):
    id: int

