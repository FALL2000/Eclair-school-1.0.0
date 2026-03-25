from datetime import date
from typing import Optional

from sqlmodel import Field, SQLModel


class PresenceEnseignantBase(SQLModel):
    date_cours: date = Field(
        description="Date du cours",
        nullable=False,
    )
    is_present: bool = Field(
        default=True,
        sa_column_kwargs={"server_default": "1"},
        description="Indique si l'enseignant était présent",
        nullable=False,
    )
    is_justifie: bool = Field(
        default=False,
        sa_column_kwargs={"server_default": "0"},
        description="Indique si l'absence est justifiée",
        nullable=False,
    )


class PresenceEnseignantCreateDTO(PresenceEnseignantBase):
    pass


class PresenceEnseignantUpdateDTO(SQLModel):
    date_cours: Optional[date] = None
    is_present: Optional[bool] = None
    is_justifie: Optional[bool] = None


class PresenceEnseignantResponseDTO(PresenceEnseignantBase):
    id: int

