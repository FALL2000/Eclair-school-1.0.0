from datetime import date
from typing import Optional

from sqlmodel import Field, SQLModel


class ReglementBase(SQLModel):
    type: str = Field(
        max_length=20, description="Type de reglement(Total ou partiel)", nullable=False)
    montant: float = Field(description="Montant du reglement", nullable=False)


class ReglementCreateDTO(ReglementBase):
    pass


class ReglementUpdateDTO(SQLModel):
    type: Optional[str] = None
    montant: Optional[float] = None


class ReglementResponseDTO(ReglementBase):
    id: int
    date_reglement: date
