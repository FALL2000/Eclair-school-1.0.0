from typing import Optional

from sqlmodel import Field, SQLModel


class AppreciationBase(SQLModel):
    libelle: str = Field(
        max_length=60,
        description="Libellé de l'appréciation",
        nullable=False,
    )
    valeur_min: float = Field(
        description="Valeur minimale pour cette appréciation",
        nullable=False,
    )
    valeur_max: float = Field(
        description="Valeur maximale pour cette appréciation",
        nullable=False,
    )


class AppreciationCreateDTO(AppreciationBase):
    pass


class AppreciationUpdateDTO(SQLModel):
    libelle: Optional[str] = None
    valeur_min: Optional[float] = None
    valeur_max: Optional[float] = None


class AppreciationResponseDTO(AppreciationBase):
    id: int

