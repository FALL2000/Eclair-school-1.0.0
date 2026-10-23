from typing import Optional

from pydantic import ConfigDict, field_validator
from sqlmodel import Field, SQLModel

from common.validators import arrondir_note


class NotationBase(SQLModel):
    note: float = Field(
        description="Note obtenue (2 décimales)",
        nullable=False,
    )
    type: str = Field(
        max_length=20,
        description="Type de notation (Primaire, Secondaire)",
        nullable=False,
    )

    @field_validator("note")
    @classmethod
    def arrondir_valeur_note(cls, value):
        return arrondir_note(value)


class NotationCreateDTO(NotationBase):
    pass


class NotationUpdateDTO(SQLModel):
    note: Optional[float] = None
    type: Optional[str] = None

    @field_validator("note")
    @classmethod
    def arrondir_valeur_note(cls, value):
        return arrondir_note(value)


class NotationItemDTO(SQLModel):
    """Note d'un élève dans une saisie en masse"""
    id_eleve: int
    note: float = Field(description="Note obtenue (2 décimales)")

    @field_validator("note")
    @classmethod
    def arrondir_valeur_note(cls, value):
        return arrondir_note(value)


class NotationBulkCreateDTO(SQLModel):
    """Saisie en masse des notes d'une classe pour une évaluation et une matière évaluée"""
    id_evaluation: int
    id_classe: int
    id_matiere_evalue: int
    notes: list[NotationItemDTO]


class NotationBulkUpdateDTO(SQLModel):
    """Modification en masse des notes d'une classe pour une évaluation et une matière évaluée"""
    id_evaluation: int
    id_classe: int
    id_matiere_evalue: int
    notes: list[NotationItemDTO]


class NotationResponseDTO(NotationBase):
    id: int
    id_eleve: int
    id_matiere_evalue: int
    id_evaluation: int
    id_classe: int
    id_annee: int
    id_appreciation: int


class EleveNotationDTO(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    matricule: str
    nom: str
    prenom: Optional[str] = None


class AppreciationNotationDTO(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    libelle: str


class NotationDetailResponseDTO(NotationResponseDTO):
    model_config = ConfigDict(from_attributes=True)

    eleve: EleveNotationDTO
    appreciation: AppreciationNotationDTO


class NotationCalculResponseDTO(SQLModel):
    """Résultat du calcul des notes d'une évaluation à partir de ses dépendances"""
    notations: list[NotationDetailResponseDTO]
    eleves_non_classes: list[int] = Field(
        description="Élèves inscrits non classés dans toutes les dépendances (aucune note calculée)")
