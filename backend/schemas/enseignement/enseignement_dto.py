from typing import List, Optional

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel

from schemas.enseignants.enseignant_dto import EnseignantCreateDTO, EnseignantResponseDTO


class EnseignementBase(SQLModel):
    unite_salaire_mt: Optional[float] = Field(
        default=None,
        description="Unité de salaire pour cet enseignement (montant horaire, etc.)",
        nullable=True,
    )


class EnseignementCreateDTO(EnseignementBase):
    pass


class EnseignementUpdateDTO(SQLModel):
    unite_salaire_mt: Optional[float] = None


class EnseignementBulkUpdateItemDTO(SQLModel):
    id: int
    unite_salaire_mt: Optional[float] = None


class EnseignementBulkUpdateDTO(SQLModel):
    enseignements: List[EnseignementBulkUpdateItemDTO]


class EnseignementBulkDeleteDTO(SQLModel):
    ids: List[int]


class EnseignementAvecEnseignantCreateDTO(SQLModel):
    enseignant: EnseignantCreateDTO
    enseignement: EnseignementCreateDTO


class EnseignementBulkItemDTO(SQLModel):
    id_matiere: int
    unite_salaire_mt: Optional[float] = None


class EnseignantAvecEnseignementsBulkCreateDTO(SQLModel):
    enseignant: EnseignantCreateDTO
    enseignements: List[EnseignementBulkItemDTO]


class EnseignementSansEnseignantBulkItemDTO(SQLModel):
    id_matiere: int
    unite_salaire_mt: Optional[float] = None


class EnseignementSansEnseignantBulkCreateDTO(SQLModel):
    items: List[EnseignementSansEnseignantBulkItemDTO]


class EnseignementResponseDTO(EnseignementBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    id_enseignant: int
    id_matiere: int


class EnseignementAvecEnseignantResponseDTO(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    enseignant: EnseignantResponseDTO
    enseignement: EnseignementResponseDTO


class EnseignantAvecEnseignementsResponseDTO(SQLModel):
    enseignant: EnseignantResponseDTO
    enseignements: List[EnseignementResponseDTO]
