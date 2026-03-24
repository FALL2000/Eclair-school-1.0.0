from typing import Optional

from sqlmodel import Field, SQLModel


class NotationBase(SQLModel):
    note: float = Field(
        description="Note obtenue",
        nullable=False,
    )
    type: str = Field(
        max_length=20,
        description="Type de notation (Primaire, Secondaire)",
        nullable=False,
    )


class NotationCreateDTO(NotationBase):
    pass


class NotationUpdateDTO(SQLModel):
    note: Optional[float] = None
    type: Optional[str] = None


class NotationResponseDTO(NotationBase):
    id: int
