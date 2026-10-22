"""Validateurs partagés par les DTO du projet."""
from typing import Optional

NB_DECIMALES_NOTE = 2


def arrondir_note(value: Optional[float]) -> Optional[float]:
    """Arrondit une note ou une borne de note à 2 chiffres après la virgule"""
    if value is None:
        return value
    return round(value, NB_DECIMALES_NOTE)
