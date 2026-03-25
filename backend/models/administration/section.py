from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship
from schemas.administration.section_dto import SectionBase

if TYPE_CHECKING:
    from models.administration.cycle import Cycle


class Section(SectionBase, table=True):
    __tablename__ = "section"

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id de la section")

    cycles: list["Cycle"] = Relationship(
        back_populates="section",
        sa_relationship_kwargs={"cascade": "all, delete"}
    )
