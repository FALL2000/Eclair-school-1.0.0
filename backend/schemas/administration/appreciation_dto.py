from typing import Optional

from pydantic import field_validator
from sqlmodel import Field, SQLModel

from common.validators import arrondir_note


class AppreciationBase(SQLModel):
    libelle: str = Field(
        max_length=60,
        description="Libellé de l'appréciation",
        nullable=False,
    )
    libelle_en: Optional[str] = Field(
        default=None,
        max_length=60,
        description="Libellé de l'appréciation en anglais (bulletins en anglais)",
        nullable=True,
    )
    valeur_min: float = Field(
        description="Valeur minimale pour cette appréciation (incluse, 2 décimales)",
        nullable=False,
    )
    valeur_max: float = Field(
        description="Valeur maximale pour cette appréciation (incluse, 2 décimales)",
        nullable=False,
    )

    @field_validator("valeur_min", "valeur_max")
    @classmethod
    def arrondir_valeurs(cls, value):
        return arrondir_note(value)


class AppreciationCreateDTO(AppreciationBase):
    pass


class AppreciationUpdateDTO(SQLModel):
    libelle: Optional[str] = None
    libelle_en: Optional[str] = Field(default=None, max_length=60)
    valeur_min: Optional[float] = None
    valeur_max: Optional[float] = None
    id_bareme: Optional[int] = None

    @field_validator("valeur_min", "valeur_max")
    @classmethod
    def arrondir_valeurs(cls, value):
        return arrondir_note(value)


class AppreciationResponseDTO(AppreciationBase):
    id: int
    id_bareme: int
