"""Modules, actions et rôles utilisés pour le contrôle des permissions.
Une permission a pour code « module:action » (ex : eleve:inscrire)."""
from enum import Enum

ROLE_SUPER_ADMIN = "SUPER ADMIN"
ROLE_ADMIN = "ADMIN"


class Action(str, Enum):
    AJOUTER = "ajouter"
    MODIFIER = "modifier"
    SUPPRIMER = "supprimer"
    CONSULTER = "consulter"
    RECHERCHER = "rechercher"
    INSCRIRE = "inscrire"
    ANNULER = "annuler"
    CALCULER = "calculer"
    GENERER = "generer"
    ATTRIBUER = "attribuer"


class Module(str, Enum):
    # Domaine administration
    ANNEE = "annee"
    CONFIGURATION = "configuration"
    SECTION = "section"
    CYCLE = "cycle"
    NIVEAU = "niveau"
    CLASSE = "classe"
    SERIE = "serie"
    TRIMESTRE = "trimestre"
    GROUPE_MATIERE = "groupe_matiere"
    MATIERE = "matiere"
    GROUPE_MATIERE_EVALUE = "groupe_matiere_evalue"
    MATIERE_EVALUE = "matiere_evalue"
    BAREME = "bareme"
    APPRECIATION = "appreciation"
    DISCIPLINE_DECISION = "discipline_decision"
    TRANCHE_PENSION = "tranche_pension"
    UTILISATEUR = "utilisateur"
    # Domaine securite (réservé au SUPER ADMIN par défaut)
    ROLE = "role"
    # Domaine eleves
    ELEVE = "eleve"
    # Domaine enseignement
    ENSEIGNANT = "enseignant"
    ENSEIGNEMENT = "enseignement"
    COURS = "cours"
    PRESENCE_ELEVE = "presence_eleve"
    PRESENCE_ENSEIGNANT = "presence_enseignant"
    SALAIRE = "salaire"
    # Domaine evaluations
    EVALUATION = "evaluation"
    NOTATION = "notation"
    DISCIPLINE_ELEVE = "discipline_eleve"
    BULLETIN = "bulletin"
    # Domaine scolarite
    REGLEMENT = "reglement"


def code_permission(module: Module, action: Action) -> str:
    return f"{module.value}:{action.value}"
