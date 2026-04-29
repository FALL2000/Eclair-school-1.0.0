from datetime import date
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
