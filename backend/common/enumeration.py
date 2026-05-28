from enum import Enum


class TypeReglement(str, Enum):
    TOTAL = "total"
    PARTIEL = "partiel"


class StatutReglement(str, Enum):
    VALIDE = "valide"
    ANNULE = "annule"


class TypeSalaire(str, Enum):
    MENSUEL = "Mensuel"
    HORAIRE = "Horaire"
