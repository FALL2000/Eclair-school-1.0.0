from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, UniqueConstraint

from schemas.evaluations.notation_dto import NotationBase

if TYPE_CHECKING:
    from models.administration.matiere_evalue import MatiereEvalue
    from models.eleve.eleve import Eleve
    from models.administration.annee import Annee
    from models.evaluations.evaluation import Evaluation
    from models.administration.appreciation import Appreciation
    from models.administration.classe import Classe


class Notation(NotationBase, table=True):
    __tablename__ = "notation"

    __table_args__ = (
        UniqueConstraint(
            "id_matiere_evalue", "id_eleve", "id_annee", "id_evaluation", "id_classe",
            name="unique_matiere_evalue_eleve_annee_classe"
        ),
    )

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Id de la notation"
    )
    id_matiere_evalue: int = Field(
        foreign_key="matiere_evalue.id",
        description="Id de la matière évaluée",
    )
    id_eleve: int = Field(
        foreign_key="eleve.id",
        description="Id de l'élève",
    )
    id_annee: int = Field(
        foreign_key="annee.id",
        description="Id de l'année scolaire",
    )
    id_evaluation: int = Field(
        foreign_key="evaluation.id",
        description="Id de l'évaluation",
    )
    id_appreciation: int = Field(
        foreign_key="appreciation.id",
        description="Id de l'appréciation",
    )
    id_classe: int = Field(
        foreign_key="classe.id",
        description="Id de la classe",
    )

    matiere_evalue: "MatiereEvalue" = Relationship(back_populates="notations")
    eleve: "Eleve" = Relationship(back_populates="notations")
    annee: "Annee" = Relationship(back_populates="notations")
    evaluation: "Evaluation" = Relationship(back_populates="notations")
    appreciation: "Appreciation" = Relationship(back_populates="notations")
    classe: "Classe" = Relationship(back_populates="notations")
