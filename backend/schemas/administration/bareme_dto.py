from typing import Optional

from pydantic import field_validator
from sqlmodel import Field, SQLModel

from common.validators import arrondir_note


class BaremeBase(SQLModel):
    code: str = Field(
        unique=True,
        max_length=10,
        description="Code unique du barème de notation",
        nullable=False,
    )
    libelle: str = Field(
        max_length=60,
        description="Libellé du barème de notation (ex: Sur 20)",
        nullable=False,
    )
    valeur_max: float = Field(
        gt=0,
        description="Note maximale du barème (ex: 20, 2 décimales)",
        nullable=False,
    )

    @field_validator("valeur_max")
    @classmethod
    def arrondir_valeur_max(cls, value):
        return arrondir_note(value)


class BaremeCreateDTO(BaremeBase):
    pass


class BaremeUpdateDTO(SQLModel):
    code: Optional[str] = None
    libelle: Optional[str] = None
    valeur_max: Optional[float] = Field(default=None, gt=0)

    @field_validator("valeur_max")
    @classmethod
    def arrondir_valeur_max(cls, value):
        return arrondir_note(value)


class BaremeResponseDTO(BaremeBase):
    id: int
