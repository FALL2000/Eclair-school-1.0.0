from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship

from schemas.administration.matiere_dto import MatiereBase

if TYPE_CHECKING:
    from models.enseignement.cours import Cours
    from models.enseignement.enseignement import Enseignement


class Matiere(MatiereBase, table=True):
    __tablename__ = "matiere"

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id de la matière"
    )

    enseignements: list["Enseignement"] = Relationship(
        back_populates="matiere", sa_relationship_kwargs={"cascade": "all, delete"})
    cours: list["Cours"] = Relationship(back_populates="matiere")
