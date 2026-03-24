from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship
from schemas.enseignants.enseignant_dto import EnseignantBase

if TYPE_CHECKING:
    from models.enseignants.type_salaire import TypeSalaire
    from models.enseignement.cours import Cours
    from models.enseignement.enseignement import Enseignement
    from models.enseignement.presence_enseignant import PresenceEnseignant


class Enseignant(EnseignantBase, table=True):
    __tablename__ = "enseignant"

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id de l'enseignant")
    is_active: bool = Field(default=True,  nullable=False,  sa_column_kwargs={
                            "server_default": "1"}, description="Indique si l'enseignant est actuellement actif dans l'établissement")
    id_type_salaire: int = Field(foreign_key="type_salaire.id")

    type_salaire: "TypeSalaire" = Relationship(back_populates="enseignants")
    enseignements: list["Enseignement"] = Relationship(
        back_populates="enseignant", sa_relationship_kwargs={"cascade": "all, delete"})
    cours: list["Cours"] = Relationship(back_populates="enseignant")
    presences: list["PresenceEnseignant"] = Relationship(
        back_populates="enseignant")
