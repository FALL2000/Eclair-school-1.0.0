from datetime import date, datetime
from typing import Optional

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel

from schemas.eleve.eleve_dto import EleveCreateDTO, EleveResponseDTO


class InscriptionBase(SQLModel):
    is_redoublant: bool = Field(
        default=False,
        sa_column_kwargs={"server_default": "0"},
        description="Indique si l'eleve est redoublant de la classe",
        nullable=False
    )
    is_nouveau: bool = Field(
        default=False,
        sa_column_kwargs={"server_default": "0"},
        description="Indique si l'eleve est nouveau dans l'etablissement",
        nullable=False
    )


class InscriptionCreateDTO(InscriptionBase):
    pass


class InscriptionUpdateDTO(SQLModel):
    is_redoublant: Optional[bool] = None
    is_nouveau: Optional[bool] = None
    id_user: Optional[int] = None


class InscriptionResponseDTO(InscriptionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date_inscris: Optional[date] = None
    is_inscris: bool
    eleve: EleveResponseDTO


class InscriptionNouveauEleveRequestDTO(InscriptionBase):
    eleve: EleveCreateDTO
    id_classe: int = Field(description="Id de la classe d'affectation")


class PaginatedInscription(SQLModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    inscriptions: list[InscriptionResponseDTO]


class InscriptionModificationDTO(SQLModel):
    """Modification d'une inscription : classe (le niveau suit la classe) et statut redoublant"""
    id_classe: Optional[int] = None
    is_redoublant: Optional[bool] = None


class InscriptionHistoriqueDTO(SQLModel):
    """Ligne de l'historique des inscriptions"""
    id: int
    date_inscris: Optional[date] = None
    is_redoublant: bool
    is_nouveau: bool
    id_eleve: int
    matricule: str
    nom: str
    prenom: Optional[str] = None
    genre: str
    dat_naissance: date
    lieu_naissance: str
    id_classe: int
    classe: str
    id_niveau: int
    niveau: str
    id_user: Optional[int] = None
    user: Optional[str] = Field(default=None, description="Utilisateur ayant fait l'inscription")
    date_modification: Optional[datetime] = None
    id_user_modification: Optional[int] = None
    user_modification: Optional[str] = Field(default=None, description="Utilisateur ayant fait la derniere modification")


class PaginatedHistoriqueInscription(SQLModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    inscriptions: list[InscriptionHistoriqueDTO]
