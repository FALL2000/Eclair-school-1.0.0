from typing import Optional

from pydantic import field_validator
from sqlmodel import Field, SQLModel

from common.validators import arrondir_note


class NotationBase(SQLModel):
    note: float = Field(
        description="Note obtenue (2 décimales)",
        nullable=False,
    )
    type: str = Field(
        max_length=20,
        description="Type de notation (Primaire, Secondaire)",
        nullable=False,
    )

    @field_validator("note")
    @classmethod
    def arrondir_valeur_note(cls, value):
        return arrondir_note(value)


class NotationCreateDTO(NotationBase):
    pass


class NotationUpdateDTO(SQLModel):
    note: Optional[float] = None
    type: Optional[str] = None

    @field_validator("note")
    @classmethod
    def arrondir_valeur_note(cls, value):
        return arrondir_note(value)


class NotationResponseDTO(NotationBase):
    id: int
