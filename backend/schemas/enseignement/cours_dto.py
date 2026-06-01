from datetime import time
from typing import List, Optional

from pydantic import ConfigDict
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


class CoursBulkCreateItemDTO(SQLModel):
    jour: str = Field(max_length=15, description="Jour du cours")
    heure_deb: time = Field(description="Heure de début")
    heure_fin: time = Field(description="Heure de fin")
    id_enseignant: int
    id_classe: int
    id_matiere: int


class CoursBulkCreateDTO(SQLModel):
    cours: List[CoursBulkCreateItemDTO]


class CoursUpdateDTO(SQLModel):
    jour: Optional[str] = None
    heure_deb: Optional[time] = None
    heure_fin: Optional[time] = None


class CoursBulkUpdateItemDTO(SQLModel):
    id: int
    jour: Optional[str] = None
    heure_deb: Optional[time] = None
    heure_fin: Optional[time] = None


class CoursBulkUpdateDTO(SQLModel):
    cours: List[CoursBulkUpdateItemDTO]


class CoursResponseDTO(CoursBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    id_enseignant: int
    id_classe: int
    id_annee: int
    id_matiere: int


# --- DTOs pour les relations ---

class MatiereBriefDTO(SQLModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    code: str
    libelle: str


class ClasseBriefDTO(SQLModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    code: str
    libelle: str


class EnseignantBriefDTO(SQLModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nom: str
    prenom: Optional[str] = None


class CoursParEnseignantResponseDTO(CoursBase):
    """Réponse pour les cours d'un enseignant : inclut matière et classe"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    id_enseignant: int
    id_classe: int
    id_annee: int
    id_matiere: int
    matiere: MatiereBriefDTO
    classe: ClasseBriefDTO


class CoursParClasseResponseDTO(CoursBase):
    """Réponse pour les cours d'une classe : inclut enseignant et matière"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    id_enseignant: int
    id_classe: int
    id_annee: int
    id_matiere: int
    enseignant: EnseignantBriefDTO
    matiere: MatiereBriefDTO
