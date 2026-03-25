from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship
from schemas.enseignants.type_salaire_dto import TypeSalaireBase

if TYPE_CHECKING:
    from models.enseignants.enseignant import Enseignant


class TypeSalaire(TypeSalaireBase, table=True):
    __tablename__ = "type_salaire"

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id du type de salaire")

    enseignants: list["Enseignant"] = Relationship(
        back_populates="type_salaire")
