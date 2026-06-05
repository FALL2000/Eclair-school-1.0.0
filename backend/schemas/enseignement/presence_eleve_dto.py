from datetime import date
from typing import Optional

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


class PresenceEleveBase(SQLModel):
    date_cours: date = Field(
        description="Date du cours",
        nullable=False,
    )
    is_present: bool = Field(
        default=True,
        sa_column_kwargs={"server_default": "1"},
        description="Indique si l'élève était présent",
        nullable=False,
    )
    is_justifie: bool = Field(
        default=False,
        sa_column_kwargs={"server_default": "0"},
        description="Indique si l'absence est justifiée",
        nullable=False,
    )


class PresenceEleveCreateDTO(PresenceEleveBase):
    pass


class PresenceEleveUpdateDTO(SQLModel):
    date_cours: Optional[date] = None
    is_present: Optional[bool] = None
    is_justifie: Optional[bool] = None


class PresenceEleveResponseDTO(PresenceEleveBase):
    id: int
    id_cours: int
    id_eleve: int


class EleveBriefDTO(SQLModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    matricule: str
    nom: str
    prenom: Optional[str] = None


class PresenceEleveWithEleveResponseDTO(PresenceEleveBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    id_cours: int
    id_eleve: int
    eleve: EleveBriefDTO


class PresenceEleveItemCreateDTO(SQLModel):
    id_eleve: int
    is_present: bool = True
    is_justifie: bool = False


class PresenceEleveBulkCreateDTO(SQLModel):
    id_cours: int
    date_cours: date
    presences: list[PresenceEleveItemCreateDTO]


class PresenceEleveItemUpdateDTO(SQLModel):
    id: int
    is_present: Optional[bool] = None
    is_justifie: Optional[bool] = None
    date_cours: Optional[date] = None


class PresenceEleveBulkUpdateDTO(SQLModel):
    presences: list[PresenceEleveItemUpdateDTO]
