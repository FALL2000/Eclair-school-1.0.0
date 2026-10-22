from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship

from schemas.administration.bareme_dto import BaremeBase

if TYPE_CHECKING:
    from models.administration.appreciation import Appreciation
    from models.administration.matiere_evalue import MatiereEvalue


class Bareme(BaremeBase, table=True):
    __tablename__ = "bareme"

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id du barème de notation"
    )

    matieres_evaluees: list["MatiereEvalue"] = Relationship(back_populates="bareme")
    appreciations: list["Appreciation"] = Relationship(back_populates="bareme")
