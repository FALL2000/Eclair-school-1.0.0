from datetime import date
from typing import Optional

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel

from common.enumeration import StatutReglement


class ReglementBase(SQLModel):
    type: str = Field(
        max_length=20, description="Type de reglement(Total ou partiel)", nullable=False)
    montant: float = Field(description="Montant du reglement", nullable=False)
    statut: StatutReglement = Field(
        default=StatutReglement.VALIDE,
        description="Statut du reglement (valide, annule)",
        nullable=False,
    )


class ReglementCreateDTO(ReglementBase):
    pass


class ReglementUpdateDTO(SQLModel):
    type: Optional[str] = None
    montant: Optional[float] = None
    statut: Optional[StatutReglement] = None


class UserReglementDTO(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom: Optional[str] = None
    prenom: Optional[str] = None


class ReglementResponseDTO(ReglementBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date_reglement: date
    id_eleve: int
    id_tranche_pension: int
    id_annee: int
    id_user: Optional[int] = None
    user: Optional[UserReglementDTO] = None


class PaginatedReglement(SQLModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    reglements: list[ReglementResponseDTO]


class EleveReglementDTO(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    matricule: str
    nom: str
    prenom: Optional[str] = None


class ReglementParClasseResponseDTO(ReglementBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date_reglement: date
    id_tranche_pension: int
    id_annee: int
    id_user: Optional[int] = None
    eleve: EleveReglementDTO
