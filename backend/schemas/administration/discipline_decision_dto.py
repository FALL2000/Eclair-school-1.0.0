from typing import Optional

from sqlmodel import Field, SQLModel


class DisciplineDecisionBase(SQLModel):
    libelle: str = Field(
        max_length=60,
        description="Libellé de la décision disciplinaire",
        nullable=False,
    )
    libelle_en: Optional[str] = Field(
        default=None,
        max_length=60,
        description="Libellé de la décision disciplinaire en anglais (bulletins en anglais)",
        nullable=True,
    )
    nb_heure_min: int = Field(
        ge=0,
        description="Nombre minimal d'heures d'absence pour cette décision",
        nullable=False,
    )
    nb_heure_max: int = Field(
        ge=0,
        description="Nombre maximal d'heures d'absence pour cette décision",
        nullable=False,
    )


class DisciplineDecisionCreateDTO(DisciplineDecisionBase):
    pass


class DisciplineDecisionUpdateDTO(SQLModel):
    libelle: Optional[str] = None
    libelle_en: Optional[str] = Field(default=None, max_length=60)
    nb_heure_min: Optional[int] = Field(default=None, ge=0)
    nb_heure_max: Optional[int] = Field(default=None, ge=0)


class DisciplineDecisionResponseDTO(DisciplineDecisionBase):
    id: int
