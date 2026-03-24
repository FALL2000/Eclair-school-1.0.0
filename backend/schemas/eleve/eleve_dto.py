from datetime import date
from typing import Optional

from sqlmodel import Field, SQLModel


class EleveBase(SQLModel):
    nom: str = Field(
        max_length=255, description="Nom de l'eleve", nullable=False)
    prenom: Optional[str] = Field(
        default=None, max_length=255, description="Prenom de l'eleve", nullable=True)
    dat_naissance: date = Field(
        description="Date de naissance de l'eleve", nullable=False)
    nom_pere: Optional[str] = Field(
        default=None, max_length=255, description="nom du pere de l'eleve", nullable=True)
    lieu_naissance: str = Field(
        max_length=255, description="Lieu de naissance de l'eleve", nullable=False)
    nom_mere: str = Field(
        max_length=255, description="Nom de la mere de l'eleve", nullable=False)
    quartier_residence: str = Field(
        max_length=255, description="quartier de residence de l'eleve", nullable=False)
    telephone_parent1: str = Field(
        max_length=20, description="Telephone du parent de l'eleve 1", nullable=False)
    telephone_parent2: Optional[str] = Field(
        default=None, max_length=20, description="Telephone du parent de l'eleve 2", nullable=True)
    genre: str = Field(
        max_length=1, description="Telephone du parent de l'eleve 2", nullable=False)


class EleveCreateDTO(EleveBase):
    pass


class EleveUpdateDTO(SQLModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    dat_naissance: Optional[date] = None
    nom_pere: Optional[str] = None
    lieu_naissance: Optional[str] = None
    nom_mere: Optional[str] = None
    quartier_residence: Optional[str] = None
    telephone_parent1: Optional[str] = None
    telephone_parent2: Optional[str] = None
    genre: Optional[str] = None


class EleveResponseDTO(EleveBase):
    id: int
    matricule: str
    is_active: bool
