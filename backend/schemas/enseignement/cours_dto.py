from datetime import time
from typing import Optional

from sqlmodel import Field, SQLModel


class CoursBase(SQLModel):
    jour: str = Field(
        max_length=15,
        description="Jour du cours (Lundi, Mardi, ...)",
        nullable=False,
    )
    heure_deb: time = Field(
        description="Heure de début du cours",
        nullable=False,
    )
    heure_fin: time = Field(
        description="Heure de fin du cours",
        nullable=False,
    )


class CoursCreateDTO(CoursBase):
    pass


class CoursUpdateDTO(SQLModel):
    jour: Optional[str] = None
    heure_deb: Optional[time] = None
    heure_fin: Optional[time] = None


class CoursResponseDTO(CoursBase):
    id: int
