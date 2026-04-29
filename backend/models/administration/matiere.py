from typing import Optional, TYPE_CHECKING
from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, Relationship

from schemas.administration.matiere_dto import MatiereBase

if TYPE_CHECKING:
    from models.enseignement.cours import Cours
    from models.enseignement.enseignement import Enseignement
    from models.administration.groupe_matiere import GroupeMatiere


class Matiere(MatiereBase, table=True):
    __tablename__ = "matiere"

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id de la matière"
    )
    id_groupe_matiere: Optional[int] = Field(
        sa_column=Column(Integer, ForeignKey(
            "groupe_matiere.id", ondelete="CASCADE")),
        description="Id du groupe de matière"
    )

    groupe_matiere: "GroupeMatiere" = Relationship(back_populates="matieres")
    enseignements: list["Enseignement"] = Relationship(
        back_populates="matiere", sa_relationship_kwargs={"cascade": "all, delete"})
    cours: list["Cours"] = Relationship(back_populates="matiere")
