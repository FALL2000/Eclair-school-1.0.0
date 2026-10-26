from datetime import date
from typing import Optional

from sqlmodel import Field, SQLModel

from common.enumeration import MoyenPaiement, StatutPaiementTranche, StatutReglement


class VersementSalaireBase(SQLModel):
    mois: int = Field(ge=1, le=12, description="Mois paye (1 a 12)", nullable=False)
    annee_civile: int = Field(description="Annee civile du mois paye (ex : 2026)", nullable=False)
    montant: float = Field(gt=0, description="Montant verse", nullable=False)


class VersementSalaireCreateDTO(VersementSalaireBase):
    id_enseignant: int
    date_versement: date = Field(description="Date a laquelle le salaire a ete verse")


class VersementSalaireResponseDTO(VersementSalaireBase):
    id: int
    id_enseignant: int
    id_annee: int
    date_versement: date
    montant_du: float = Field(description="Salaire du mois au moment du versement")
    nb_heures: Optional[float] = Field(default=None, description="Heures payees (salaire horaire) au moment du versement")
    statut: StatutReglement
    id_user: Optional[int] = None


class SalaireMoisDTO(SQLModel):
    """Situation du salaire d'un enseignant pour un mois"""
    id_enseignant: int
    nom: str
    prenom: Optional[str] = None
    is_active: bool = Field(description="L'enseignant est-il actif dans l'etablissement")
    type_salaire: str
    is_horaire: bool
    taux: Optional[float] = Field(default=None, description="Salaire mensuel ou taux horaire")
    nb_heures: Optional[float] = Field(default=None, description="Heures payees du mois (salaire horaire)")
    montant_du: float
    montant_verse: float
    reste: float
    statut_paiement: StatutPaiementTranche
    moyen_paiement: Optional[MoyenPaiement] = Field(default=None, description="None : moyen de paiement pas encore configure")


class SalaireEnseignantDetailDTO(SalaireMoisDTO):
    mois: int
    annee_civile: int
    numero_compte: Optional[str] = Field(default=None, description="Complet avec salaire:ajouter ou salaire:modifier, sinon masque")
    intitule_compte: Optional[str] = None
    versements: list[VersementSalaireResponseDTO]


class PaginatedSalaireMois(SQLModel):
    mois: int
    annee_civile: int
    total_du: float
    total_verse: float
    total_reste: float
    page: int
    page_size: int
    total_items: int
    total_pages: int
    salaires: list[SalaireMoisDTO]


class VersementSalaireDetailDTO(VersementSalaireResponseDTO):
    """Versement avec l'enseignant et l'utilisateur qui l'a enregistre"""
    nom: str
    prenom: Optional[str] = None
    user: Optional[str] = Field(default=None, description="Utilisateur ayant enregistre le versement")


class PaginatedVersementSalaire(SQLModel):
    total_verse: float = Field(description="Somme des versements valides correspondant aux filtres")
    page: int
    page_size: int
    total_items: int
    total_pages: int
    versements: list[VersementSalaireDetailDTO]


class MoyenPaiementUpdateDTO(SQLModel):
    """Configuration du moyen de paiement du salaire d'un enseignant"""
    moyen_paiement: MoyenPaiement = Field(description="ESPECE, COMPTE BANCAIRE ou MOBILE")
    numero_compte: Optional[str] = Field(
        default=None, max_length=60, description="Obligatoire si COMPTE BANCAIRE ou MOBILE, ignore si ESPECE")
    intitule_compte: Optional[str] = Field(default=None, max_length=255, description="Intitule du compte (titulaire)")


class MoyenPaiementEnseignantDTO(SQLModel):
    id_enseignant: int
    nom: str
    prenom: Optional[str] = None
    telephone1: Optional[str] = None
    type_salaire: str
    moyen_paiement: Optional[MoyenPaiement] = Field(default=None, description="None : pas encore configure")
    numero_compte: Optional[str] = Field(default=None, description="Complet avec salaire:ajouter ou salaire:modifier, sinon masque")
    intitule_compte: Optional[str] = None


class PaginatedMoyenPaiement(SQLModel):
    nb_non_configures: int = Field(description="Nombre d'enseignants actifs sans moyen de paiement (tous filtres confondus)")
    page: int
    page_size: int
    total_items: int
    total_pages: int
    enseignants: list[MoyenPaiementEnseignantDTO]
