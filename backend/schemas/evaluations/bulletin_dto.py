from datetime import date
from typing import Optional

from sqlmodel import Field, SQLModel


# ---------- Requête du bulletin annuel ----------

class RegleDecisionDTO(SQLModel):
    """Décision de fin d'année attribuée aux élèves dont la moyenne annuelle est dans [moyenne_min, moyenne_max]"""
    moyenne_min: float = Field(ge=0, le=20)
    moyenne_max: float = Field(ge=0, le=20)
    decision: str = Field(max_length=100, description="Ex : Promu, Promu en cas de..., Redouble")


class BulletinAnnuelRequestDTO(SQLModel):
    seuil_reussite: float = Field(ge=0, le=20, description="Moyenne annuelle minimale pour réussir")
    regles_decision: list[RegleDecisionDTO]


# ---------- Statistiques ----------

class StatistiquesDTO(SQLModel):
    effectif: int
    moyenne: Optional[float] = None
    plus_haute: Optional[float] = None
    plus_basse: Optional[float] = None
    ecart_type: Optional[float] = None
    mediane: Optional[float] = None
    nb_reussite: int
    taux_reussite: Optional[float] = None


class TrancheRepartitionDTO(SQLModel):
    libelle: str
    effectif: int
    pourcentage: Optional[float] = None


class StatistiquesGenreDTO(SQLModel):
    genre: str
    effectif: int
    moyenne: Optional[float] = None
    nb_reussite: int
    taux_reussite: Optional[float] = None


class EffectifDecisionDTO(SQLModel):
    decision: str
    effectif: int


class StatistiquesDisciplineDTO(SQLModel):
    total_heures: int
    total_heures_justifiees: int
    total_heures_non_justifiees: int
    moyenne_heures_par_eleve: Optional[float] = None
    moyenne_heures_non_justifiees_par_eleve: Optional[float] = Field(
        default=None, description="Heures non justifiées par élève (base des décisions disciplinaires)")
    decisions: list[EffectifDecisionDTO]


class StatistiquesClasseDTO(SQLModel):
    effectif_inscrits: int
    effectif_classes: int
    effectif_non_classes: int
    moyenne_classe: Optional[float] = None
    moyenne_premier: Optional[float] = None
    moyenne_dernier: Optional[float] = None
    ecart_type: Optional[float] = None
    mediane: Optional[float] = None
    nb_reussite: int
    taux_reussite: Optional[float] = None
    nb_tableau_honneur: Optional[int] = None
    repartition: list[TrancheRepartitionDTO]
    par_genre: list[StatistiquesGenreDTO]
    discipline: StatistiquesDisciplineDTO
    decisions_fin_annee: Optional[list[EffectifDecisionDTO]] = None


class StatistiquesMatiereDTO(SQLModel):
    id_matiere_evalue: int
    code: str
    libelle: str
    statistiques: StatistiquesDTO


# ---------- Bulletin d'un élève ----------

class EleveBulletinDTO(SQLModel):
    id: int
    matricule: str
    nom: str
    prenom: Optional[str] = None
    genre: str
    dat_naissance: date
    lieu_naissance: str
    is_redoublant: bool


class NoteEvaluationDTO(SQLModel):
    """Note d'une matière pour une évaluation affichée en colonne (évaluation du trimestre ou dépendance)"""
    id_evaluation: int
    note: Optional[float] = Field(default=None, description="Note dans le barème de la matière")
    note_sur_20: Optional[float] = None


class EvaluationColonneDTO(SQLModel):
    """Évaluation affichée en colonne sur le bulletin"""
    id_evaluation: int
    code: str
    libelle: str
    pourcentage: Optional[float] = Field(default=None, description="Poids de la dépendance dans l'évaluation (bulletin d'évaluation)")


class LigneMatiereDTO(SQLModel):
    id_matiere_evalue: int
    code: str
    libelle: str
    note: Optional[float] = Field(default=None, description="Note dans le barème de la matière (bulletin d'évaluation)")
    bareme: Optional[float] = None
    note_sur_20: Optional[float] = None
    coefficient: int
    points: Optional[float] = Field(default=None, description="note sur 20 x coefficient")
    rang: Optional[int] = None
    rang_libelle: Optional[str] = None
    appreciation: Optional[str] = None
    notes_evaluations: list[NoteEvaluationDTO] = Field(
        default=[], description="Notes des évaluations de entete.evaluations, dans le même ordre")


class GroupeBulletinDTO(SQLModel):
    id: int
    code: str
    libelle: str
    lignes: list[LigneMatiereDTO]
    total_coefficients: int
    total_points: Optional[float] = None
    moyenne: Optional[float] = None
    rang: Optional[int] = None
    rang_libelle: Optional[str] = None
    appreciation: Optional[str] = None


class DisciplineBulletinDTO(SQLModel):
    nb_heure_obtenu: int
    nb_heure_justifie: int
    nb_heure_total: int
    decision: Optional[str] = None


class MoyenneTrimestreDTO(SQLModel):
    id_trimestre: int
    libelle: str
    moyenne: Optional[float] = None


class BulletinEleveDTO(SQLModel):
    eleve: EleveBulletinDTO
    groupes: list[GroupeBulletinDTO]
    total_coefficients: int
    total_points: Optional[float] = None
    moyenne_generale: Optional[float] = None
    rang: Optional[int] = None
    rang_libelle: Optional[str] = None
    appreciation: Optional[str] = None
    is_reussite: Optional[bool] = None
    distinction: Optional[str] = None
    discipline: DisciplineBulletinDTO
    moyennes_trimestres: Optional[list[MoyenneTrimestreDTO]] = None
    decision_fin_annee: Optional[str] = None


# ---------- Bulletins d'une classe ----------

class EnteteBulletinDTO(SQLModel):
    type_bulletin: str = Field(description="evaluation, trimestre ou annuel")
    type_school: str
    annee: str
    id_classe: int
    classe: str
    periode: Optional[str] = Field(default=None, description="Libellé de l'évaluation ou du trimestre")
    seuil_reussite: float
    date_generation: date
    langue: str = Field(default="FR", description="Langue du bulletin : FR ou EN")
    evaluations: list[EvaluationColonneDTO] = Field(
        default=[], description="Colonnes de notes : évaluations du trimestre (bulletin trimestriel), "
                                "évaluations de l'année (bulletin annuel) "
                                "ou dépendances de l'évaluation (bulletin d'évaluation calculée)")


class BulletinClasseDTO(SQLModel):
    entete: EnteteBulletinDTO
    statistiques_classe: StatistiquesClasseDTO
    statistiques_matieres: list[StatistiquesMatiereDTO]
    bulletins: list[BulletinEleveDTO]
