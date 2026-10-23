"""Validateurs partagés par les DTO du projet."""
from typing import Optional

NB_DECIMALES_NOTE = 2


def arrondir_note(value: Optional[float]) -> Optional[float]:
    """Arrondit une note ou une borne de note à 2 chiffres après la virgule"""
    if value is None:
        return value
    return round(value, NB_DECIMALES_NOTE)


def arrondir_note_calculee(value: float) -> float:
    """Arrondit une note calculée automatiquement au quart de point selon sa partie décimale :
    - 0.00 à 0.19 -> valeur entière (9.15 -> 9)
    - 0.20 à 0.30 -> .25 (9.26 -> 9.25)
    - 0.31 à 0.59 -> .5 (9.41 -> 9.5)
    - 0.60 à 0.79 -> .75 (9.61 -> 9.75)
    - 0.80 à 0.99 -> valeur entière suivante (9.81 -> 10)
    La note est d'abord ramenée à 2 décimales, puis le calcul se fait en centièmes entiers
    pour éviter les imprécisions des nombres à virgule."""
    centiemes = round(value * 100)
    entier, decimale = divmod(centiemes, 100)
    if decimale < 20:
        quart = 0
    elif decimale <= 30:
        quart = 25
    elif decimale < 60:
        quart = 50
    elif decimale < 80:
        quart = 75
    else:
        quart = 100
    return (entier * 100 + quart) / 100
