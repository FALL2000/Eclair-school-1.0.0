from datetime import date
from typing import Optional

from sqlmodel import Field, SQLModel


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


class InscriptionResponseDTO(InscriptionBase):
    id: int
    date_inscris: date
