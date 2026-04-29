from typing import Optional

from sqlmodel import Field, SQLModel


class GroupeMatiereBase(SQLModel):
    libelle: str = Field(
        unique=True,
        max_length=60,
        description="Libellé du groupe de matières",
        nullable=False,
    )


class GroupeMatiereCreateDTO(GroupeMatiereBase):
    pass


class GroupeMatiereUpdateDTO(SQLModel):
    libelle: Optional[str] = None


class GroupeMatiereResponseDTO(GroupeMatiereBase):
    id: int




