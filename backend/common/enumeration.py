from enum import Enum


class TypeReglement(str, Enum):
    TOTAL = "total"
    PARTIEL = "partiel"


class StatutReglement(str, Enum):
    VALIDE = "valide"
    ANNULE = "annule"


class StatutPaiementTranche(str, Enum):
    TOTAL = "total"
    PARTIEL = "partiel"
    AUCUN = "aucun"


class MoyenPaiement(str, Enum):
    """Moyen de paiement du salaire d'un enseignant"""
    ESPECE = "ESPECE"
    COMPTE_BANCAIRE = "COMPTE BANCAIRE"
    MOBILE = "MOBILE"


# Moyens de paiement pour lesquels le numero de compte est obligatoire
MOYENS_PAIEMENT_AVEC_COMPTE = (MoyenPaiement.COMPTE_BANCAIRE, MoyenPaiement.MOBILE)


class Langue(str, Enum):
    """Langue de génération d'un document (bulletin)"""
    FR = "FR"
    EN = "EN"


class TypeNotation(str, Enum):
    PRIMAIRE = "Primaire"
    SECONDAIRE = "Secondaire"


# Correspondance entre type_school (.env) et le type de notation enregistré
TYPE_NOTATION_PAR_TYPE_SCHOOL = {
    "education_base": TypeNotation.PRIMAIRE,
    "secondaire": TypeNotation.SECONDAIRE,
}


class TypeSalaire(str, Enum):
    MENSUEL = "Mensuel"
    HORAIRE = "Horaire"
