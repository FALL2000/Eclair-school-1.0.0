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
