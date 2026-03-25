from typing import Optional

from sqlmodel import Field, SQLModel


class EnseignantBase(SQLModel):
    nom: str = Field(
        max_length=255, description="Nom de l'enseignant", nullable=False)
    prenom: Optional[str] = Field(
        default=None, max_length=255, description="Nom de l'enseignant", nullable=True)
    dernier_diplome: str = Field(
        max_length=60, description="Dernier diplome de l'enseignant", nullable=False)
    genre: str = Field(
        max_length=1, description="genre de l'enseignant", nullable=False)
    telephone1: str = Field(
        max_length=60, description="Telephone de l'enseignant 1", nullable=False)
    telephone2: Optional[str] = Field(
        default=None, max_length=60, description="Telephone de l'enseignant 2", nullable=True)
    montant_salaire: Optional[float] = Field(
        default=None, description="Salaire mensuel de l'enseignant", nullable=True)


class EnseignantCreateDTO(EnseignantBase):
    pass


class EnseignantUpdateDTO(SQLModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    dernier_diplome: Optional[str] = None
    genre: Optional[str] = None
    telephone1: Optional[str] = None
    telephone2: Optional[str] = None
    montant_salaire: Optional[float] = None


class EnseignantResponseDTO(EnseignantBase):
    id: int
    is_active: bool
