from datetime import date
from typing import Optional

from pydantic import field_validator
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
        max_length=1, description="genre de l'eleve", nullable=False)

    @field_validator("genre")
    @classmethod
    def genre_must_be_valid(cls, value):
        if value is not None and value not in ['M', 'F']:
            raise ValueError("le genre doit avoir la valeur 'M' ou 'F'")
        return value


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
    is_active: Optional[bool] = Field(
        default=None, description="Indique si l'eleve est actif dans l'etablissement")

    @field_validator("genre")
    @classmethod
    def genre_must_be_valid(cls, value):
        if value is not None and value not in ['M', 'F']:
            raise ValueError("le genre doit avoir la valeur 'M' ou 'F'")
        return value


class EleveResponseDTO(EleveBase):
    id: int
    matricule: str
    is_active: bool


class EleveRechercheResponseDTO(SQLModel):
    """Résultat de la recherche d'un élève dans toute l'école"""
    id: int
    matricule: str
    nom: str
    prenom: Optional[str] = None
    genre: str
    dat_naissance: date
    lieu_naissance: str
    id_classe: Optional[int] = Field(default=None, description="Classe de l'année en cours (vide si non inscrit)")
    classe: Optional[str] = Field(default=None, description="Libellé de la classe de l'année en cours")


class EleveClasseResponseDTO(EleveResponseDTO):
    """Élève inscrit dans une classe pour l'année en cours"""
    id_inscription: int
    is_redoublant: bool
    is_nouveau: bool
    date_inscris: Optional[date] = None


class PaginatedEleveClasse(SQLModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    eleves: list[EleveClasseResponseDTO]
