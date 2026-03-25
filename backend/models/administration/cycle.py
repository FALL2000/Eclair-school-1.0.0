from typing import Optional, TYPE_CHECKING
from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, Relationship
from schemas.administration.cycle_dto import CycleBase

if TYPE_CHECKING:
    from models.administration.section import Section
    from models.administration.niveau import Niveau


class Cycle(CycleBase, table=True):
    __tablename__ = "cycle"

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id du cycle")
    id_section: int = Field(
        sa_column=Column(Integer, ForeignKey(
            "section.id", ondelete="CASCADE")),
        description="Id de la section"
    )

    section: "Section" = Relationship(back_populates="cycles")
    niveaux: list["Niveau"] = Relationship(
        back_populates="cycle", sa_relationship_kwargs={"cascade": "all, delete"})
