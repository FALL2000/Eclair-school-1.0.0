from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, UniqueConstraint

from schemas.evaluations.discipline_eleve_dto import DisciplineEleveBase

if TYPE_CHECKING:
    from models.eleve.eleve import Eleve
    from models.administration.annee import Annee
    from models.administration.classe import Classe
    from models.evaluations.evaluation import Evaluation


class DisciplineEleve(DisciplineEleveBase, table=True):
    __tablename__ = "discipline_eleve"

    __table_args__ = (
        UniqueConstraint(
            "id_eleve", "id_annee", "id_classe", "id_evaluation",
            name="unique_eleve_annee_classe_evaluation"
        ),
    )

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id de la discipline de l'élève"
    )
    id_eleve: int = Field(
        foreign_key="eleve.id",
        description="Id de l'élève",
    )
    id_annee: int = Field(
        foreign_key="annee.id",
        description="Id de l'année scolaire",
    )
    id_classe: int = Field(
        foreign_key="classe.id",
        description="Id de la classe",
    )
    id_evaluation: int = Field(
        foreign_key="evaluation.id",
        description="Id de l'évaluation",
    )

    eleve: "Eleve" = Relationship(back_populates="disciplines")
    annee: "Annee" = Relationship(back_populates="disciplines")
    classe: "Classe" = Relationship(back_populates="disciplines")
    evaluation: "Evaluation" = Relationship(back_populates="disciplines")
