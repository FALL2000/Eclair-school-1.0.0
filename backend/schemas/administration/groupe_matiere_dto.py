from typing import List, Optional

from sqlmodel import Field, SQLModel

from schemas.administration.matiere_dto import MatiereResponseDTO


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


class GroupeMatiereReadWithMatiere(GroupeMatiereResponseDTO):
    matieres: List[MatiereResponseDTO]
