"""Données initiales des rôles et des permissions.

À copier dans la migration Alembic qui suit la migration de structure
(tables permission, role_permission et colonne role.is_systeme) :
  - copier les imports, les constantes et les fonctions ci-dessous dans le fichier de migration ;
  - appeler upgrade_data() à la fin de upgrade() et downgrade_data() au début de downgrade().

Contenu :
  - le catalogue des permissions (code « module:action ») ;
  - les rôles de base SUPER ADMIN (toutes les permissions, sans vérification) et ADMIN
    (toutes les permissions du domaine administration) ;
  - le premier SUPER ADMIN, si SUPER_ADMIN_USERNAME et SUPER_ADMIN_PASSWORD sont renseignés dans le .env :
    l'utilisateur est créé s'il n'existe pas, sinon le rôle lui est simplement attribué ;
  - les types de salaire des enseignants (Mensuel, Horaire), seulement ceux qui n'existent pas encore.
"""
from alembic import op
import sqlalchemy as sa

from config.settings import get_settings
from security.password_hacher import hash_password

ID_ROLE_SUPER_ADMIN = 1
ID_ROLE_ADMIN = 2
ROLES = [
    {"id": ID_ROLE_SUPER_ADMIN, "role_name": "SUPER ADMIN", "is_systeme": True},
    {"id": ID_ROLE_ADMIN, "role_name": "ADMIN", "is_systeme": True},
]
DOMAINE_ADMIN = "administration"

# Libellés identiques à l'énumération TypeSalaire (common/enumeration.py)
TYPES_SALAIRE = [
    {"code": "MENSUEL", "libelle": "Mensuel"},
    {"code": "HORAIRE", "libelle": "Horaire"},
]

CRUD = ["ajouter", "modifier", "supprimer", "consulter"]
VERBES = {
    "ajouter": "Ajouter", "modifier": "Modifier", "supprimer": "Supprimer", "consulter": "Consulter",
    "rechercher": "Rechercher", "inscrire": "Inscrire", "annuler": "Annuler", "calculer": "Calculer",
    "generer": "Générer", "attribuer": "Attribuer",
}

# domaine -> [(module, complément du libellé, actions)]
CATALOGUE_PERMISSIONS = {
    "administration": [
        ("annee", "une année scolaire", ["ajouter", "modifier", "consulter"]),
        ("configuration", "la configuration", ["ajouter", "modifier", "consulter"]),
        ("section", "une section", CRUD),
        ("cycle", "un cycle", CRUD),
        ("niveau", "un niveau", CRUD),
        ("classe", "une classe", CRUD),
        ("serie", "une série", CRUD),
        ("trimestre", "un trimestre", CRUD),
        ("groupe_matiere", "un groupe de matières", CRUD),
        ("matiere", "une matière", CRUD),
        ("groupe_matiere_evalue", "un groupe de matières évaluées", CRUD),
        ("matiere_evalue", "une matière évaluée", CRUD),
        ("bareme", "un barème de notation", CRUD),
        ("appreciation", "une appréciation", CRUD),
        ("discipline_decision", "une décision disciplinaire", CRUD),
        ("tranche_pension", "une tranche de pension", CRUD),
        ("utilisateur", "un utilisateur", CRUD),
    ],
    "securite": [
        ("role", "un rôle", CRUD + ["attribuer"]),
    ],
    "eleves": [
        ("eleve", "un élève", ["ajouter", "inscrire", "modifier", "consulter", "rechercher"]),
    ],
    "enseignement": [
        ("enseignant", "un enseignant", CRUD + ["rechercher"]),
        ("enseignement", "une affectation enseignant-matière", CRUD),
        ("cours", "un cours", CRUD),
        ("presence_eleve", "la présence des élèves", ["ajouter", "modifier", "consulter"]),
        ("presence_enseignant", "la présence des enseignants", ["ajouter", "modifier", "consulter"]),
        # salaire:modifier = configurer le moyen de paiement (compte) des enseignants
        ("salaire", "le salaire des enseignants", ["ajouter", "modifier", "annuler", "consulter"]),
    ],
    "evaluations": [
        ("evaluation", "une évaluation", CRUD),
        ("notation", "des notes", ["ajouter", "modifier", "consulter", "calculer"]),
        ("discipline_eleve", "la discipline des élèves", ["ajouter", "modifier", "consulter", "calculer"]),
        ("bulletin", "les bulletins", ["generer"]),
    ],
    "scolarite": [
        ("reglement", "un règlement", ["ajouter", "modifier", "annuler", "consulter", "rechercher"]),
    ],
}


def construire_permissions() -> list[dict]:
    permissions = []
    for domaine, modules in CATALOGUE_PERMISSIONS.items():
        for module, complement, actions in modules:
            for action in actions:
                permissions.append({
                    "id": len(permissions) + 1,
                    "code": f"{module}:{action}",
                    "module": module,
                    "action": action,
                    "domaine": domaine,
                    "libelle": f"{VERBES[action]} {complement}",
                })
    return permissions


def upgrade_data() -> None:
    permission_table = sa.table(
        "permission",
        sa.column("id", sa.Integer), sa.column("code", sa.String), sa.column("module", sa.String),
        sa.column("action", sa.String), sa.column("domaine", sa.String), sa.column("libelle", sa.String),
    )
    role_table = sa.table(
        "role", sa.column("id", sa.Integer), sa.column("role_name", sa.String), sa.column("is_systeme", sa.Boolean),
    )
    role_permission_table = sa.table(
        "role_permission", sa.column("id_role", sa.Integer), sa.column("id_permission", sa.Integer),
    )
    user_table = sa.table(
        "user", sa.column("id", sa.Integer), sa.column("username", sa.String), sa.column("password", sa.String),
    )
    user_role_table = sa.table("user_role", sa.column("id_user", sa.Integer), sa.column("id_role", sa.Integer))

    permissions = construire_permissions()
    op.bulk_insert(permission_table, permissions)
    op.bulk_insert(role_table, ROLES)
    # ADMIN : toutes les permissions du domaine administration
    op.bulk_insert(role_permission_table, [
        {"id_role": ID_ROLE_ADMIN, "id_permission": p["id"]} for p in permissions if p["domaine"] == DOMAINE_ADMIN
    ])

    # Premier SUPER ADMIN (optionnel)
    settings = get_settings()
    if settings.super_admin_username and settings.super_admin_password:
        connexion = op.get_bind()
        selection = sa.select(user_table.c.id).where(user_table.c.username == settings.super_admin_username)
        id_user = connexion.execute(selection).scalar()
        if id_user is None:
            connexion.execute(user_table.insert().values(
                username=settings.super_admin_username,
                password=hash_password(settings.super_admin_password),
            ))
            id_user = connexion.execute(selection).scalar()
        connexion.execute(user_role_table.insert().values(id_user=id_user, id_role=ID_ROLE_SUPER_ADMIN))

    # Types de salaire : seuls ceux qui n'existent pas encore sont ajoutés
    type_salaire_table = sa.table(
        "type_salaire", sa.column("code", sa.String), sa.column("libelle", sa.String),
    )
    codes_existants = set(op.get_bind().execute(sa.select(type_salaire_table.c.code)).scalars())
    nouveaux_types = [t for t in TYPES_SALAIRE if t["code"] not in codes_existants]
    if nouveaux_types:
        op.bulk_insert(type_salaire_table, nouveaux_types)


def downgrade_data() -> None:
    # Les types de salaire déjà utilisés par des enseignants sont conservés
    codes = ", ".join(f"'{t['code']}'" for t in TYPES_SALAIRE)
    op.execute(
        f"DELETE FROM type_salaire WHERE code IN ({codes}) "
        "AND id NOT IN (SELECT id_type_salaire FROM enseignant)"
    )
    op.execute("DELETE FROM role_permission")
    op.execute(f"DELETE FROM user_role WHERE id_role IN ({ID_ROLE_SUPER_ADMIN}, {ID_ROLE_ADMIN})")
    op.execute(f"DELETE FROM role WHERE id IN ({ID_ROLE_SUPER_ADMIN}, {ID_ROLE_ADMIN})")
    op.execute("DELETE FROM permission")
