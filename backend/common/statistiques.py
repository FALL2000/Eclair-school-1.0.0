"""Fonctions statistiques utilisées pour les bulletins.
Fonctions pures : une liste de nombres en entrée, un résultat en sortie (aucun accès à la BD)."""
import math
from typing import Hashable, Optional

NB_DECIMALES = 2


def arrondir(value: Optional[float]) -> Optional[float]:
    """Arrondit à 2 décimales (None reste None)"""
    if value is None:
        return None
    return round(value, NB_DECIMALES)


def moyenne(valeurs: list[float]) -> Optional[float]:
    if not valeurs:
        return None
    return sum(valeurs) / len(valeurs)


def ecart_type(valeurs: list[float]) -> Optional[float]:
    """Écart type de la population : toute la classe est prise en compte, ce n'est pas un échantillon"""
    if not valeurs:
        return None
    m = moyenne(valeurs)
    return math.sqrt(sum((v - m) ** 2 for v in valeurs) / len(valeurs))


def mediane(valeurs: list[float]) -> Optional[float]:
    if not valeurs:
        return None
    tri = sorted(valeurs)
    milieu = len(tri) // 2
    if len(tri) % 2:
        return tri[milieu]
    return (tri[milieu - 1] + tri[milieu]) / 2


def calculer_rangs(valeurs: dict[Hashable, float]) -> dict[Hashable, tuple[int, bool]]:
    """Classe les valeurs par ordre décroissant.
    Les ex æquo partagent le même rang et le rang suivant est sauté (1, 2, 2, 4).
    Retourne {clé: (rang, ex_aequo)}"""
    occurrences: dict[float, int] = {}
    for valeur in valeurs.values():
        occurrences[valeur] = occurrences.get(valeur, 0) + 1
    rangs = {}
    rang_courant = 0
    valeur_precedente = None
    tri = sorted(valeurs.items(), key=lambda item: item[1], reverse=True)
    for position, (cle, valeur) in enumerate(tri, start=1):
        if valeur != valeur_precedente:
            rang_courant = position
            valeur_precedente = valeur
        rangs[cle] = (rang_courant, occurrences[valeur] > 1)
    return rangs


def statistiques(valeurs: list[float], seuil_reussite: float) -> dict:
    """Statistiques d'une série de notes ou de moyennes"""
    nb_reussite = sum(1 for v in valeurs if v >= seuil_reussite)
    return {
        "effectif": len(valeurs),
        "moyenne": arrondir(moyenne(valeurs)),
        "plus_haute": arrondir(max(valeurs)) if valeurs else None,
        "plus_basse": arrondir(min(valeurs)) if valeurs else None,
        "ecart_type": arrondir(ecart_type(valeurs)),
        "mediane": arrondir(mediane(valeurs)),
        "nb_reussite": nb_reussite,
        "taux_reussite": arrondir(nb_reussite * 100 / len(valeurs)) if valeurs else None,
    }


def repartition(valeurs: list[float], tranches: list[tuple[float, float, str]]) -> list[dict]:
    """Répartition des valeurs par tranche (min inclus, max exclu, libellé)"""
    total = len(valeurs)
    resultat = []
    for valeur_min, valeur_max, libelle in tranches:
        effectif = sum(1 for v in valeurs if valeur_min <= v < valeur_max)
        resultat.append({
            "libelle": libelle,
            "effectif": effectif,
            "pourcentage": arrondir(effectif * 100 / total) if total else None,
        })
    return resultat
