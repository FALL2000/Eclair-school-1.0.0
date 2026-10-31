import re
from typing import Optional

from pydantic import field_validator
from sqlmodel import Field, SQLModel

# Code d'une année scolaire : deux années consécutives, ex. 2026-2027
FORMAT_ANNEE = re.compile(r"^(\d{4})-(\d{4})$")


def verifier_code_annee(code: Optional[str]) -> Optional[str]:
    """Vérifie que le code est de la forme AAAA-AAAA avec deux années consécutives"""
    if code is None:
        return code
    code = code.strip()
    correspondance = FORMAT_ANNEE.match(code)
    if correspondance is None or int(correspondance.group(2)) != int(correspondance.group(1)) + 1:
        raise ValueError(
            "Le code doit être de la forme AAAA-AAAA avec deux années consécutives (ex. 2026-2027)")
    return code


class AnneeBase(SQLModel):
    code: str = Field(
        unique=True, max_length=10, description="Code unique de l'annee", nullable=False)
    libelle: str = Field(
        max_length=60, description="Libelle de l'annee", nullable=False)


class AnneeCreateDTO(AnneeBase):
    """Première année scolaire du système (les suivantes sont calculées automatiquement)"""

    @field_validator("code")
    @classmethod
    def verifier_code(cls, value):
        return verifier_code_annee(value)


class AnneeUpdateDTO(SQLModel):
    code: Optional[str] = None
    libelle: Optional[str] = None
    is_cloture: Optional[bool] = Field(
        default=None, description="True pour clôturer l'année en cours (une année clôturée ne peut pas être rouverte)")

    @field_validator("code")
    @classmethod
    def verifier_code(cls, value):
        return verifier_code_annee(value)


class AnneeResponseDTO(AnneeBase):
    id: int
    is_cloture: bool
