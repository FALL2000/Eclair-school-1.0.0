from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship
from schemas.administration.serie_dto import SerieBase

if TYPE_CHECKING:
    from models.administration.niveau import Niveau


class Serie(SerieBase, table=True):
    __tablename__ = "serie"

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id de la serie")

    niveaux: list["Niveau"] = Relationship(
        back_populates="serie",
        sa_relationship_kwargs={"cascade": "save-update, merge"}
    )
