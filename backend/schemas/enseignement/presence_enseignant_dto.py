from datetime import date, time
from typing import Optional

from sqlmodel import Field, SQLModel


class PresenceEnseignantBase(SQLModel):
    date_cours: date = Field(
        description="Date du cours",
        nullable=False,
    )
    is_present: bool = Field(
        default=True,
        sa_column_kwargs={"server_default": "1"},
        description="Indique si l'enseignant était présent",
        nullable=False,
    )
    is_justifie: bool = Field(
        default=False,
        sa_column_kwargs={"server_default": "0"},
        description="Indique si l'absence est justifiée",
        nullable=False,
    )


class PresenceEnseignantCreateDTO(PresenceEnseignantBase):
    pass


class PresenceEnseignantUpdateDTO(SQLModel):
    date_cours: Optional[date] = None
    is_present: Optional[bool] = None
    is_justifie: Optional[bool] = None


class PresenceEnseignantResponseDTO(PresenceEnseignantBase):
    id: int
    id_cours: int
    id_enseignant: int


class PresenceCoursSaisieDTO(SQLModel):
    """Presence de l'enseignant d'un cours (absence justifiee seulement si absent)"""
    id_cours: int
    is_present: bool = True
    is_justifie: bool = False


class PresencesJourSaveDTO(SQLModel):
    date_cours: date = Field(description="Date des cours (pas dans le futur)")
    presences: list[PresenceCoursSaisieDTO]


class CoursPresenceDTO(SQLModel):
    """Cours planifie a la date choisie, avec la presence de son enseignant si elle est deja saisie"""
    id_cours: int
    heure_deb: time
    heure_fin: time
    id_classe: int
    classe: str
    id_matiere: int
    matiere: str
    id_enseignant: int
    nom: str
    prenom: Optional[str] = None
    id_presence: Optional[int] = Field(default=None, description="None : presence pas encore saisie")
    is_present: Optional[bool] = None
    is_justifie: Optional[bool] = None


class PresencesJourDTO(SQLModel):
    date_cours: date
    jour: str
    nb_saisies: int
    nb_absents: int
    cours: list[CoursPresenceDTO]
