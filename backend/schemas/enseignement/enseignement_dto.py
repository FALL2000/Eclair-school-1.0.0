from typing import Optional

from sqlmodel import Field, SQLModel


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


class EnseignementResponseDTO(EnseignementBase):
    id: int

