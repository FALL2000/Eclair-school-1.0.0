from datetime import date

from fastapi import HTTPException

from common.enumeration import Langue, TYPE_NOTATION_PAR_TYPE_SCHOOL, TypeNotation
from common.statistiques import arrondir, calculer_rangs, moyenne, repartition, statistiques
from config.settings import get_settings
from models.evaluations.evaluation import Evaluation
from repositories.administration.annee_repository import AnneeRepository
from repositories.administration.appreciation_repository import AppreciationRepository
from repositories.administration.bareme_repository import BaremeRepository
from repositories.administration.classe_repository import ClasseRepository
from repositories.administration.configuration_repository import ConfigurationRepository
from repositories.administration.discipline_decision_repository import DisciplineDecisionRepository
from repositories.administration.groupe_matiere_evalue_repository import GroupeMatiereEvalueRepository
from repositories.administration.matiere_evalue_repository import MatiereEvalueRepository
from repositories.administration.trimestre_repository import TrimestreRepository
from repositories.evaluations.depends_evaluation_repository import DependsEvaluationRepository
from repositories.evaluations.discipline_eleve_repository import DisciplineEleveRepository
from repositories.evaluations.evaluation_repository import EvaluationRepository
from repositories.evaluations.notation_repository import NotationRepository
from repositories.inscription.inscription_repository import InscriptionRepository
from schemas.evaluations.bulletin_dto import BulletinAnnuelRequestDTO
from services.administration.annee_service import AnneeService

BASE_NOTE = 20
SEUIL_REUSSITE = 10
SEUIL_TABLEAU_HONNEUR = 12
TABLEAU_HONNEUR = "Tableau d'honneur"

# Appréciations utilisées pour les moyennes sur 20 quand aucun barème sur 20 n'a d'appréciations
APPRECIATIONS_PAR_DEFAUT = [
    (0, 4.99, "Très faible"),
    (5, 7.99, "Faible"),
    (8, 9.99, "Insuffisant"),
    (10, 11.99, "Passable"),
    (12, 13.99, "Assez bien"),
    (14, 15.99, "Bien"),
    (16, 17.99, "Très bien"),
    (18, 20, "Excellent"),
]
APPRECIATIONS_PAR_DEFAUT_EN = [
    (0, 4.99, "Very poor"),
    (5, 7.99, "Poor"),
    (8, 9.99, "Insufficient"),
    (10, 11.99, "Fair"),
    (12, 13.99, "Fairly good"),
    (14, 15.99, "Good"),
    (16, 17.99, "Very good"),
    (18, 20, "Excellent"),
]


def libelle_selon_langue(objet, langue: Langue) -> str:
    """Libellé anglais (libelle_en) si le bulletin est en anglais et qu'il est renseigné, sinon le libellé français"""
    if langue == Langue.EN and getattr(objet, "libelle_en", None):
        return objet.libelle_en
    return objet.libelle

TRANCHES_REPARTITION = [
    (0, 5, "[0 ; 5["),
    (5, 8, "[5 ; 8["),
    (8, 10, "[8 ; 10["),
    (10, 12, "[10 ; 12["),
    (12, 14, "[12 ; 14["),
    (14, 16, "[14 ; 16["),
    (16, float("inf"), "[16 ; 20]"),
]


class BulletinService:
    """Calcule les données des bulletins d'une classe (par évaluation, par trimestre ou annuel).
    Les notes sont ramenées sur 20 ; une matière sans note est « non classée » (ignorée, ce n'est pas un 0)."""

    def __init__(
        self,
        annee_repository: AnneeRepository,
        classe_repository: ClasseRepository,
        inscription_repository: InscriptionRepository,
        evaluation_repository: EvaluationRepository,
        depends_evaluation_repository: DependsEvaluationRepository,
        trimestre_repository: TrimestreRepository,
        notation_repository: NotationRepository,
        matiere_evalue_repository: MatiereEvalueRepository,
        groupe_matiere_evalue_repository: GroupeMatiereEvalueRepository,
        bareme_repository: BaremeRepository,
        appreciation_repository: AppreciationRepository,
        discipline_eleve_repository: DisciplineEleveRepository,
        discipline_decision_repository: DisciplineDecisionRepository,
        configuration_repository: ConfigurationRepository,
    ):
        self.annee_repository = annee_repository
        self.classe_repository = classe_repository
        self.inscription_repository = inscription_repository
        self.evaluation_repository = evaluation_repository
        self.depends_evaluation_repository = depends_evaluation_repository
        self.trimestre_repository = trimestre_repository
        self.notation_repository = notation_repository
        self.matiere_evalue_repository = matiere_evalue_repository
        self.groupe_matiere_evalue_repository = groupe_matiere_evalue_repository
        self.bareme_repository = bareme_repository
        self.appreciation_repository = appreciation_repository
        self.discipline_eleve_repository = discipline_eleve_repository
        self.discipline_decision_repository = discipline_decision_repository
        self.configuration_repository = configuration_repository

    def _get_annee_service(self):
        return AnneeService(self.annee_repository)

    # ------------------------------------------------------------------
    # Chargement des données
    # ------------------------------------------------------------------

    def _is_primaire(self) -> bool:
        type_school = get_settings().type_school.strip().lower()
        return TYPE_NOTATION_PAR_TYPE_SCHOOL.get(type_school) == TypeNotation.PRIMAIRE

    def _get_appreciations_reference(self, langue: Langue = Langue.FR) -> list[tuple[float, float, str]]:
        """Appréciations d'un barème sur 20 s'il en existe, sinon les appréciations par défaut (dans la langue du bulletin)"""
        for bareme in self.bareme_repository.findAll():
            if bareme.valeur_max == BASE_NOTE:
                appreciations = self.appreciation_repository.findBy(id_bareme=bareme.id)
                if appreciations:
                    return [(a.valeur_min, a.valeur_max, libelle_selon_langue(a, langue)) for a in appreciations]
        return APPRECIATIONS_PAR_DEFAUT_EN if langue == Langue.EN else APPRECIATIONS_PAR_DEFAUT

    def _get_contexte_classe(self, id_classe: int, langue: Langue = Langue.FR) -> dict:
        """Charge en une fois tout ce dont les bulletins d'une classe ont besoin pour l'année en cours"""
        annee = self._get_annee_service().get_annee_scolaire()[0]
        classe = self.classe_repository.findOne(id_classe)
        if classe is None:
            raise HTTPException(
                status_code=404,
                detail={"error_code": "CLASSE_NOT_FOUND", "message": "Classe non trouvée"},
            )
        is_primaire = self._is_primaire()
        baremes = {b.id: b for b in self.bareme_repository.findAll()}

        programme = []
        groupes = sorted(
            self.groupe_matiere_evalue_repository.findBy(id_niveau=classe.id_niveau), key=lambda g: g.id)
        for groupe in groupes:
            matieres = sorted(
                self.matiere_evalue_repository.findBy(id_groupe_matiere=groupe.id), key=lambda m: m.id)
            programme.append({
                "id": groupe.id,
                "code": groupe.code,
                "libelle": groupe.libelle,
                "matieres": [
                    {
                        "id": m.id,
                        "code": m.code,
                        "libelle": m.libelle,
                        # Primaire : pas de coefficient (1) ; secondaire : coefficient de la matière (1 si vide)
                        "coefficient": 1 if is_primaire else (m.coefficient or 1),
                        "bareme": baremes.get(m.id_bareme),
                    }
                    for m in matieres
                ],
            })

        inscriptions = sorted(
            self.inscription_repository.findBy(
                load_relations=True, id_classe=id_classe, id_annee=annee.id, is_inscris=True),
            key=lambda i: (i.eleve.nom, i.eleve.prenom or ""),
        )
        notations = self.notation_repository.findBy(load_relations=True, id_classe=id_classe, id_annee=annee.id)
        avec_discipline = self.configuration_repository.is_discipline_geree()
        disciplines = (
            self.discipline_eleve_repository.findBy(id_classe=id_classe, id_annee=annee.id) if avec_discipline else []
        )

        return {
            "annee": annee,
            "classe": classe,
            "programme": programme,
            "matieres": {m["id"]: m for g in programme for m in g["matieres"]},
            "inscriptions": inscriptions,
            "notes": {(n.id_evaluation, n.id_eleve, n.id_matiere_evalue): n for n in notations},
            "disciplines": {(d.id_evaluation, d.id_eleve): d for d in disciplines},
            "decisions": self.discipline_decision_repository.findAll() if avec_discipline else [],
            "avec_discipline": avec_discipline,
            "appreciations_reference": self._get_appreciations_reference(langue),
            "langue": langue,
        }

    def _get_evaluation(self, id_evaluation: int) -> Evaluation:
        evaluation = self.evaluation_repository.findOne(id_evaluation)
        if evaluation is None:
            raise HTTPException(
                status_code=404,
                detail={"error_code": "EVALUATION_NOT_FOUND", "message": "Évaluation non trouvée"},
            )
        return evaluation

    def _get_evaluations_trimestre(self, id_trimestre: int) -> list[Evaluation]:
        """Évaluations d'un trimestre prises en compte : les dépendances d'une évaluation parente
        sont exclues, seul le parent compte"""
        evaluations = self.evaluation_repository.findBy(id_trimestre=id_trimestre)
        ids_dependances = {
            lien.id_dependance
            for evaluation in evaluations
            for lien in self.depends_evaluation_repository.findBy(id_evaluation=evaluation.id)
        }
        return sorted(
            [e for e in evaluations if e.id not in ids_dependances],
            key=lambda e: e.date_deb,
        )

    # ------------------------------------------------------------------
    # Notes
    # ------------------------------------------------------------------

    def _ramener_sur_20(self, note: float, bareme) -> float:
        """Les notes sur 20 (cas habituel au secondaire) sont gardées telles quelles"""
        if bareme is None or bareme.valeur_max == BASE_NOTE:
            return note
        return arrondir(note * BASE_NOTE / bareme.valeur_max)

    def _get_notes_evaluation(self, ctx: dict, id_evaluation: int) -> tuple[dict, dict]:
        """Retourne ({id_eleve: {id_matiere: note sur 20}}, {id_eleve: {id_matiere: notation}})"""
        notes_sur_20, notations = {}, {}
        for inscription in ctx["inscriptions"]:
            id_eleve = inscription.id_eleve
            notes_sur_20[id_eleve], notations[id_eleve] = {}, {}
            for id_matiere, matiere in ctx["matieres"].items():
                notation = ctx["notes"].get((id_evaluation, id_eleve, id_matiere))
                if notation is not None:
                    notes_sur_20[id_eleve][id_matiere] = self._ramener_sur_20(notation.note, matiere["bareme"])
                    notations[id_eleve][id_matiere] = notation
        return notes_sur_20, notations

    def _get_notes_periode(self, ctx: dict, evaluations: list[Evaluation]) -> dict:
        """Note de chaque matière sur une période = moyenne simple des notes sur 20 des évaluations
        (une évaluation sans note est ignorée). Retourne {id_eleve: {id_matiere: note sur 20}}"""
        notes_sur_20 = {}
        for inscription in ctx["inscriptions"]:
            id_eleve = inscription.id_eleve
            notes_sur_20[id_eleve] = {}
            for id_matiere, matiere in ctx["matieres"].items():
                notes = [
                    self._ramener_sur_20(n.note, matiere["bareme"])
                    for n in (ctx["notes"].get((e.id, id_eleve, id_matiere)) for e in evaluations)
                    if n is not None
                ]
                if notes:
                    notes_sur_20[id_eleve][id_matiere] = arrondir(moyenne(notes))
        return notes_sur_20

    def _calculer_moyenne(self, notes_eleve: dict, matieres: list[dict]) -> tuple[int, float | None, float | None]:
        """(total des coefficients, total des points, moyenne) sur les matières notées"""
        notees = [m for m in matieres if m["id"] in notes_eleve]
        if not notees:
            return 0, None, None
        total_coefficients = sum(m["coefficient"] for m in notees)
        total_points = sum(notes_eleve[m["id"]] * m["coefficient"] for m in notees)
        return total_coefficients, arrondir(total_points), arrondir(total_points / total_coefficients)

    # ------------------------------------------------------------------
    # Appréciations, rangs, discipline
    # ------------------------------------------------------------------

    def _get_appreciation(self, valeur: float | None, appreciations: list[tuple[float, float, str]]) -> str | None:
        if valeur is None:
            return None
        for valeur_min, valeur_max, libelle in appreciations:
            if valeur_min <= valeur <= valeur_max:
                return libelle
        return None

    def _libelle_rang(self, rang: int, ex_aequo: bool, genre: str, langue: Langue = Langue.FR) -> str:
        if langue == Langue.EN:
            # 1st, 2nd, 3rd, 4th... 11th, 12th, 13th, 21st, 22nd...
            suffixe = "th" if 10 <= rang % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(rang % 10, "th")
            libelle = f"{rang}{suffixe}"
            return f"{libelle} tie" if ex_aequo else libelle
        if rang == 1:
            libelle = "1ère" if genre == "F" else "1er"
        else:
            libelle = f"{rang}e"
        return f"{libelle} ex" if ex_aequo else libelle

    def _get_decision_discipline(self, nb_heure_non_justifie: int, decisions: list, langue: Langue = Langue.FR) -> str | None:
        """Décision dont l'intervalle contient le nombre d'heures d'absence non justifiées"""
        for decision in decisions:
            if decision.nb_heure_min <= nb_heure_non_justifie <= decision.nb_heure_max:
                return libelle_selon_langue(decision, langue)
        return None

    def _get_discipline(self, ctx: dict, id_eleve: int, evaluations: list[Evaluation]) -> dict:
        """Cumul des heures d'absence de l'élève sur les évaluations (dépendances déjà exclues) ;
        la décision disciplinaire porte sur les heures NON justifiées (nb_heure_obtenu).
        None quand l'établissement ne gère pas la discipline (pas de partie discipline au bulletin)"""
        if not ctx["avec_discipline"]:
            return None
        enregistrements = [
            d for d in (ctx["disciplines"].get((e.id, id_eleve)) for e in evaluations) if d is not None
        ]
        obtenu = sum(d.nb_heure_obtenu for d in enregistrements)
        justifie = sum(d.nb_heure_justifie for d in enregistrements)
        total = sum(d.nb_heure_total for d in enregistrements)
        return {
            "nb_heure_obtenu": obtenu,
            "nb_heure_justifie": justifie,
            "nb_heure_total": total,
            "decision": self._get_decision_discipline(obtenu, ctx["decisions"], ctx["langue"]) if enregistrements else None,
        }

    # ------------------------------------------------------------------
    # Construction des bulletins et des statistiques
    # ------------------------------------------------------------------

    def _construire_bulletins(
        self,
        ctx: dict,
        notes_sur_20: dict,
        disciplines: dict,
        entete: dict,
        avec_distinction: bool,
        notations: dict | None = None,
        moyennes_imposees: dict | None = None,
        complements: dict | None = None,
    ) -> dict:
        """Construit les bulletins de la classe et ses statistiques.
        notations : notes d'origine (bulletin d'évaluation) pour afficher la note et l'appréciation du barème
        moyennes_imposees : moyennes générales déjà calculées (bulletin annuel = moyenne des trimestres)
        complements : champs supplémentaires par élève (bulletin annuel)"""
        seuil = entete["seuil_reussite"]
        appreciations_ref = ctx["appreciations_reference"]
        ids_colonnes = [c["id_evaluation"] for c in entete.get("evaluations", [])]
        toutes_matieres = list(ctx["matieres"].values())
        bulletins = {}

        for inscription in ctx["inscriptions"]:
            eleve = inscription.eleve
            notes_eleve = notes_sur_20.get(eleve.id, {})
            groupes = []
            for groupe in ctx["programme"]:
                lignes = []
                for matiere in groupe["matieres"]:
                    note_sur_20 = notes_eleve.get(matiere["id"])
                    notation = (notations or {}).get(eleve.id, {}).get(matiere["id"])
                    notes_colonnes = []
                    for id_ev in ids_colonnes:
                        n = ctx["notes"].get((id_ev, eleve.id, matiere["id"]))
                        notes_colonnes.append({
                            "id_evaluation": id_ev,
                            "note": n.note if n is not None else None,
                            "note_sur_20": self._ramener_sur_20(n.note, matiere["bareme"]) if n is not None else None,
                        })
                    lignes.append({
                        "notes_evaluations": notes_colonnes,
                        "id_matiere_evalue": matiere["id"],
                        "code": matiere["code"],
                        "libelle": matiere["libelle"],
                        "note": notation.note if notation is not None else None,
                        "bareme": matiere["bareme"].valeur_max if matiere["bareme"] is not None else None,
                        "note_sur_20": note_sur_20,
                        "coefficient": matiere["coefficient"],
                        "points": arrondir(note_sur_20 * matiere["coefficient"]) if note_sur_20 is not None else None,
                        "rang": None,
                        "rang_libelle": None,
                        "appreciation": (
                            libelle_selon_langue(notation.appreciation, ctx["langue"]) if notation is not None
                            else self._get_appreciation(note_sur_20, appreciations_ref)
                        ),
                    })
                total_coefficients, total_points, moyenne_groupe = self._calculer_moyenne(
                    notes_eleve, groupe["matieres"])
                groupes.append({
                    "id": groupe["id"],
                    "code": groupe["code"],
                    "libelle": groupe["libelle"],
                    "lignes": lignes,
                    "total_coefficients": total_coefficients,
                    "total_points": total_points,
                    "moyenne": moyenne_groupe,
                    "rang": None,
                    "rang_libelle": None,
                    "appreciation": self._get_appreciation(moyenne_groupe, appreciations_ref),
                })

            total_coefficients, total_points, moyenne_generale = self._calculer_moyenne(notes_eleve, toutes_matieres)
            if moyennes_imposees is not None:
                moyenne_generale = moyennes_imposees.get(eleve.id)
            bulletins[eleve.id] = {
                "eleve": {
                    "id": eleve.id,
                    "matricule": eleve.matricule,
                    "nom": eleve.nom,
                    "prenom": eleve.prenom,
                    "genre": eleve.genre,
                    "dat_naissance": eleve.dat_naissance,
                    "lieu_naissance": eleve.lieu_naissance,
                    "is_redoublant": inscription.is_redoublant,
                },
                "groupes": groupes,
                "total_coefficients": total_coefficients,
                "total_points": total_points,
                "moyenne_generale": moyenne_generale,
                "rang": None,
                "rang_libelle": None,
                "appreciation": self._get_appreciation(moyenne_generale, appreciations_ref),
                "is_reussite": moyenne_generale >= seuil if moyenne_generale is not None else None,
                "distinction": (
                    TABLEAU_HONNEUR
                    if avec_distinction and moyenne_generale is not None and moyenne_generale >= SEUIL_TABLEAU_HONNEUR
                    else None
                ),
                "discipline": disciplines[eleve.id],
                **((complements or {}).get(eleve.id, {})),
            }

        self._attribuer_rangs(bulletins, ctx["langue"])
        return {
            "entete": entete,
            "statistiques_classe": self._statistiques_classe(bulletins, seuil, avec_distinction),
            "statistiques_matieres": self._statistiques_matieres(ctx, notes_sur_20, seuil),
            "bulletins": list(bulletins.values()),
        }

    def _attribuer_rangs(self, bulletins: dict, langue: Langue = Langue.FR):
        """Rang général, rang par groupe et rang par matière (seuls les élèves classés sont rangés)"""
        genres = {id_eleve: b["eleve"]["genre"] for id_eleve, b in bulletins.items()}

        def appliquer(valeurs: dict, cible):
            for id_eleve, (rang, ex_aequo) in calculer_rangs(valeurs).items():
                element = cible(id_eleve)
                element["rang"] = rang
                element["rang_libelle"] = self._libelle_rang(rang, ex_aequo, genres[id_eleve], langue)

        appliquer(
            {i: b["moyenne_generale"] for i, b in bulletins.items() if b["moyenne_generale"] is not None},
            lambda i: bulletins[i],
        )
        premier = next(iter(bulletins.values()), None)
        if premier is None:
            return
        for index_groupe, groupe in enumerate(premier["groupes"]):
            appliquer(
                {i: b["groupes"][index_groupe]["moyenne"] for i, b in bulletins.items()
                 if b["groupes"][index_groupe]["moyenne"] is not None},
                lambda i, g=index_groupe: bulletins[i]["groupes"][g],
            )
            for index_ligne in range(len(groupe["lignes"])):
                appliquer(
                    {i: b["groupes"][index_groupe]["lignes"][index_ligne]["note_sur_20"] for i, b in bulletins.items()
                     if b["groupes"][index_groupe]["lignes"][index_ligne]["note_sur_20"] is not None},
                    lambda i, g=index_groupe, l=index_ligne: bulletins[i]["groupes"][g]["lignes"][l],
                )

    def _effectifs_par_libelle(self, libelles: list[str | None]) -> list[dict]:
        effectifs: dict[str, int] = {}
        for libelle in libelles:
            if libelle is not None:
                effectifs[libelle] = effectifs.get(libelle, 0) + 1
        return [{"decision": libelle, "effectif": effectif} for libelle, effectif in effectifs.items()]

    def _statistiques_classe(self, bulletins: dict, seuil: float, avec_distinction: bool) -> dict:
        liste = list(bulletins.values())
        moyennes = [b["moyenne_generale"] for b in liste if b["moyenne_generale"] is not None]
        stats = statistiques(moyennes, seuil)

        par_genre = []
        for genre in ("M", "F"):
            moyennes_genre = [
                b["moyenne_generale"] for b in liste
                if b["eleve"]["genre"] == genre and b["moyenne_generale"] is not None
            ]
            stats_genre = statistiques(moyennes_genre, seuil)
            par_genre.append({
                "genre": genre,
                "effectif": stats_genre["effectif"],
                "moyenne": stats_genre["moyenne"],
                "nb_reussite": stats_genre["nb_reussite"],
                "taux_reussite": stats_genre["taux_reussite"],
            })

        # Discipline non gérée : chaque bulletin a discipline = None, pas de statistiques de discipline
        avec_discipline = all(b["discipline"] is not None for b in liste)
        total = sum(b["discipline"]["nb_heure_total"] for b in liste) if avec_discipline else 0
        justifiees = sum(b["discipline"]["nb_heure_justifie"] for b in liste) if avec_discipline else 0
        non_justifiees = sum(b["discipline"]["nb_heure_obtenu"] for b in liste) if avec_discipline else 0
        decisions_fin_annee = [b.get("decision_fin_annee") for b in liste]

        return {
            "effectif_inscrits": len(liste),
            "effectif_classes": stats["effectif"],
            "effectif_non_classes": len(liste) - stats["effectif"],
            "moyenne_classe": stats["moyenne"],
            "moyenne_premier": stats["plus_haute"],
            "moyenne_dernier": stats["plus_basse"],
            "ecart_type": stats["ecart_type"],
            "mediane": stats["mediane"],
            "nb_reussite": stats["nb_reussite"],
            "taux_reussite": stats["taux_reussite"],
            "nb_tableau_honneur": (
                sum(1 for m in moyennes if m >= SEUIL_TABLEAU_HONNEUR) if avec_distinction else None
            ),
            "repartition": repartition(moyennes, TRANCHES_REPARTITION),
            "par_genre": par_genre,
            "discipline": None if not avec_discipline else {
                "total_heures": total,
                "total_heures_justifiees": justifiees,
                "total_heures_non_justifiees": non_justifiees,
                "moyenne_heures_par_eleve": arrondir(total / len(liste)) if liste else None,
                "moyenne_heures_non_justifiees_par_eleve": arrondir(non_justifiees / len(liste)) if liste else None,
                "decisions": self._effectifs_par_libelle([b["discipline"]["decision"] for b in liste]),
            },
            "decisions_fin_annee": (
                self._effectifs_par_libelle(decisions_fin_annee) if any(decisions_fin_annee) else None
            ),
        }

    def _statistiques_matieres(self, ctx: dict, notes_sur_20: dict, seuil: float) -> list[dict]:
        resultat = []
        for groupe in ctx["programme"]:
            for matiere in groupe["matieres"]:
                notes = [
                    notes_eleve[matiere["id"]] for notes_eleve in notes_sur_20.values() if matiere["id"] in notes_eleve
                ]
                resultat.append({
                    "id_matiere_evalue": matiere["id"],
                    "code": matiere["code"],
                    "libelle": matiere["libelle"],
                    "statistiques": statistiques(notes, seuil),
                })
        return resultat

    @staticmethod
    def _colonne(evaluation: Evaluation, pourcentage: float | None = None) -> dict:
        return {"id_evaluation": evaluation.id, "code": evaluation.code, "libelle": evaluation.libelle, "pourcentage": pourcentage}

    def _colonnes_dependances(self, evaluation: Evaluation) -> list[dict]:
        """Dépendances d'une évaluation calculée (ex : Devoir 40 % + Composition 60 %), par date de début"""
        colonnes = []
        for lien in self.depends_evaluation_repository.findBy(id_evaluation=evaluation.id):
            dependance = self.evaluation_repository.findOne(lien.id_dependance)
            if dependance is not None:
                colonnes.append((dependance.date_deb, self._colonne(dependance, lien.pourcentage)))
        return [c for _, c in sorted(colonnes, key=lambda x: x[0])]

    def _entete(self, ctx: dict, type_bulletin: str, periode: str | None, seuil: float,
                evaluations: list[dict] | None = None) -> dict:
        return {
            "type_bulletin": type_bulletin,
            "type_school": get_settings().type_school,
            "annee": ctx["annee"].libelle,
            "id_classe": ctx["classe"].id,
            "classe": ctx["classe"].libelle,
            "periode": periode,
            "seuil_reussite": seuil,
            "date_generation": date.today(),
            "langue": ctx["langue"].value,
            "avec_discipline": ctx["avec_discipline"],
            "evaluations": evaluations or [],
        }

    def _filtrer_eleve(self, resultat: dict, id_eleve: int | None) -> dict:
        """Garde un seul bulletin (le rang et les statistiques restent calculés sur toute la classe)"""
        if id_eleve is None:
            return resultat
        bulletins = [b for b in resultat["bulletins"] if b["eleve"]["id"] == id_eleve]
        if not bulletins:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "ELEVE_NON_INSCRIT",
                    "message": "L'élève n'est pas inscrit dans cette classe pour l'année en cours",
                },
            )
        return {**resultat, "bulletins": bulletins}

    # ------------------------------------------------------------------
    # Bulletins par évaluation, trimestre et année
    # ------------------------------------------------------------------

    def generer_bulletins_evaluation(self, id_classe: int, id_evaluation: int, id_eleve: int | None = None,
                                     langue: Langue = Langue.FR) -> dict:
        """Bulletins d'une évaluation : seuil de réussite 10, pas de distinction"""
        try:
            ctx = self._get_contexte_classe(id_classe, langue)
            evaluation = self._get_evaluation(id_evaluation)
            notes_sur_20, notations = self._get_notes_evaluation(ctx, id_evaluation)
            disciplines = {
                i.id_eleve: self._get_discipline(ctx, i.id_eleve, [evaluation]) for i in ctx["inscriptions"]
            }
            resultat = self._construire_bulletins(
                ctx, notes_sur_20, disciplines,
                self._entete(ctx, "evaluation", evaluation.libelle, SEUIL_REUSSITE,
                             self._colonnes_dependances(evaluation)),
                avec_distinction=False,
                notations=notations,
            )
            return self._filtrer_eleve(resultat, id_eleve)
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la génération des bulletins de l'évaluation: {str(e)}")

    def generer_bulletins_trimestre(self, id_classe: int, id_trimestre: int, id_eleve: int | None = None,
                                    langue: Langue = Langue.FR) -> dict:
        """Bulletins d'un trimestre : note d'une matière = moyenne simple des évaluations du trimestre
        (dépendances exclues), seuil de réussite 10, tableau d'honneur à partir de 12"""
        try:
            ctx = self._get_contexte_classe(id_classe, langue)
            trimestre = self.trimestre_repository.findOne(id_trimestre)
            if trimestre is None:
                raise HTTPException(
                    status_code=404,
                    detail={"error_code": "TRIMESTRE_NOT_FOUND", "message": "Trimestre non trouvé"},
                )
            evaluations = self._get_evaluations_trimestre(id_trimestre)
            if not evaluations:
                raise HTTPException(
                    status_code=400,
                    detail={"error_code": "TRIMESTRE_SANS_EVALUATION", "message": "Le trimestre n'a aucune évaluation"},
                )
            notes_sur_20 = self._get_notes_periode(ctx, evaluations)
            disciplines = {
                i.id_eleve: self._get_discipline(ctx, i.id_eleve, evaluations) for i in ctx["inscriptions"]
            }
            resultat = self._construire_bulletins(
                ctx, notes_sur_20, disciplines,
                self._entete(ctx, "trimestre", trimestre.libelle, SEUIL_REUSSITE,
                             [self._colonne(e) for e in evaluations]),
                avec_distinction=True,
            )
            return self._filtrer_eleve(resultat, id_eleve)
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la génération des bulletins du trimestre: {str(e)}")

    def _check_regles_decision(self, data: BulletinAnnuelRequestDTO):
        regles = sorted(data.regles_decision, key=lambda r: r.moyenne_min)
        for index, regle in enumerate(regles):
            if regle.moyenne_min > regle.moyenne_max:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error_code": "REGLE_DECISION_INVALIDE",
                        "message": f"Règle « {regle.decision} » : la moyenne minimale doit être inférieure ou égale à la moyenne maximale",
                    },
                )
            if index > 0 and regle.moyenne_min <= regles[index - 1].moyenne_max:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error_code": "REGLE_DECISION_CHEVAUCHEMENT",
                        "message": f"Les règles « {regles[index - 1].decision} » et « {regle.decision} » se chevauchent",
                    },
                )

    def _get_decision_fin_annee(self, moyenne_annuelle: float | None, data: BulletinAnnuelRequestDTO) -> str | None:
        if moyenne_annuelle is None:
            return None
        for regle in data.regles_decision:
            if regle.moyenne_min <= moyenne_annuelle <= regle.moyenne_max:
                return regle.decision
        return None

    def generer_bulletins_annuels(self, id_classe: int, data: BulletinAnnuelRequestDTO, id_eleve: int | None = None,
                                  langue: Langue = Langue.FR) -> dict:
        """Bulletins annuels : moyenne annuelle = moyenne des moyennes trimestrielles ;
        note annuelle d'une matière = moyenne de ses notes trimestrielles ;
        seuil de réussite et règles de décision de fin d'année fournis par la requête"""
        try:
            self._check_regles_decision(data)
            ctx = self._get_contexte_classe(id_classe, langue)
            ids_eleves = [i.id_eleve for i in ctx["inscriptions"]]
            toutes_matieres = list(ctx["matieres"].values())

            trimestres = []
            for trimestre in sorted(self.trimestre_repository.findAll(), key=lambda t: t.id):
                evaluations = self._get_evaluations_trimestre(trimestre.id)
                if not evaluations:
                    continue
                notes_trimestre = self._get_notes_periode(ctx, evaluations)
                trimestres.append({
                    "trimestre": trimestre,
                    "evaluations": evaluations,
                    "notes": notes_trimestre,
                    "moyennes": {
                        id_e: self._calculer_moyenne(notes_trimestre[id_e], toutes_matieres)[2] for id_e in ids_eleves
                    },
                })
            if not trimestres:
                raise HTTPException(
                    status_code=400,
                    detail={"error_code": "ANNEE_SANS_EVALUATION", "message": "Aucune évaluation n'est définie dans les trimestres"},
                )

            notes_annuelles, moyennes_annuelles, complements, disciplines = {}, {}, {}, {}
            toutes_evaluations = [e for t in trimestres for e in t["evaluations"]]
            for id_e in ids_eleves:
                notes_annuelles[id_e] = {}
                for id_matiere in ctx["matieres"]:
                    notes = [t["notes"][id_e][id_matiere] for t in trimestres if id_matiere in t["notes"][id_e]]
                    if notes:
                        notes_annuelles[id_e][id_matiere] = arrondir(moyenne(notes))
                moyennes_trimestres = [t["moyennes"][id_e] for t in trimestres if t["moyennes"][id_e] is not None]
                moyennes_annuelles[id_e] = arrondir(moyenne(moyennes_trimestres))
                complements[id_e] = {
                    "moyennes_trimestres": [
                        {"id_trimestre": t["trimestre"].id, "libelle": t["trimestre"].libelle, "moyenne": t["moyennes"][id_e]}
                        for t in trimestres
                    ],
                    "decision_fin_annee": self._get_decision_fin_annee(moyennes_annuelles[id_e], data),
                }
                disciplines[id_e] = self._get_discipline(ctx, id_e, toutes_evaluations)

            resultat = self._construire_bulletins(
                ctx, notes_annuelles, disciplines,
                self._entete(ctx, "annuel", None, data.seuil_reussite,
                             [self._colonne(e) for e in toutes_evaluations]),
                avec_distinction=True,
                moyennes_imposees=moyennes_annuelles,
                complements=complements,
            )
            return self._filtrer_eleve(resultat, id_eleve)
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la génération des bulletins annuels: {str(e)}")
