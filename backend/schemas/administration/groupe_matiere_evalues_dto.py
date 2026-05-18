from typing import List, Optional

from sqlmodel import Field, SQLModel

from schemas.administration.matiere_evalue_dto import MatiereEvalueResponseDTO


class GroupeMatiereEvalueBase(SQLModel):
    code: str = Field(
        unique=True,
        max_length=160,
        description="Code unique du groupe de matières evaluées",
        nullable=False,
    )
    libelle: str = Field(
        max_length=60,
        description="Libellé du groupe de matières evaluées",
        nullable=False,
    )


class GroupeMatiereEvalueCreateDTO(GroupeMatiereEvalueBase):
    pass


class GroupeMatiereEvalueUpdateDTO(SQLModel):
    code: Optional[str] = None
    libelle: Optional[str] = None


class GroupeMatiereEvalueResponseDTO(GroupeMatiereEvalueBase):
    id: int


class GroupeMatiereEvalueReadWithMatiere(GroupeMatiereEvalueResponseDTO):
    matiere_evalues: List[MatiereEvalueResponseDTO]
