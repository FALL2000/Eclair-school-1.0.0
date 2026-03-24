from typing import Optional

from sqlmodel import Field, SQLModel


class TranchePensionBase(SQLModel):
    code: str = Field(
        unique=True, max_length=10, description="Code unique de la tranche de pension", nullable=False)
    libelle: str = Field(
        max_length=60, description="Libelle de la tranche de pension", nullable=False)
    numero_ordre: int = Field(
        description="rang de la tranche(1ere, 2e etc..)", nullable=False)
    montant: float = Field(description="Montant de la tranche", nullable=False)


class TranchePensionCreateDTO(TranchePensionBase):
    pass


class TranchePensionUpdateDTO(SQLModel):
    code: Optional[str] = None
    libelle: Optional[str] = None
    numero_ordre: Optional[int] = None
    montant: Optional[float] = None


class TranchePensionResponseDTO(TranchePensionBase):
    id: int
