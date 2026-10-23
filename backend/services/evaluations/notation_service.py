from fastapi import HTTPException

from common.enumeration import TYPE_NOTATION_PAR_TYPE_SCHOOL, TypeNotation
from common.validators import arrondir_note_calculee
from config.settings import get_settings
from models.administration.bareme import Bareme
from models.evaluations.notation import Notation
from repositories.administration.annee_repository import AnneeRepository
from repositories.administration.appreciation_repository import AppreciationRepository
from repositories.administration.bareme_repository import BaremeRepository
from repositories.administration.classe_repository import ClasseRepository
from repositories.administration.groupe_matiere_evalue_repository import GroupeMatiereEvalueRepository
from repositories.administration.matiere_evalue_repository import MatiereEvalueRepository
from repositories.evaluations.depends_evaluation_repository import DependsEvaluationRepository
from repositories.evaluations.evaluation_repository import EvaluationRepository
from repositories.evaluations.notation_repository import NotationRepository
from repositories.inscription.inscription_repository import InscriptionRepository
from schemas.evaluations.notation_dto import (
    NotationBulkCreateDTO,
    NotationBulkUpdateDTO,
    NotationItemDTO,
)
from services.administration.annee_service import AnneeService


class NotationService:
    def __init__(
        self,
        notation_repository: NotationRepository,
        evaluation_repository: EvaluationRepository,
        classe_repository: ClasseRepository,
        matiere_evalue_repository: MatiereEvalueRepository,
        groupe_matiere_evalue_repository: GroupeMatiereEvalueRepository,
        bareme_repository: BaremeRepository,
        appreciation_repository: AppreciationRepository,
        inscription_repository: InscriptionRepository,
        annee_repository: AnneeRepository,
        depends_evaluation_repository: DependsEvaluationRepository,
    ):
        self.notation_repository = notation_repository
        self.evaluation_repository = evaluation_repository
        self.classe_repository = classe_repository
        self.matiere_evalue_repository = matiere_evalue_repository
        self.groupe_matiere_evalue_repository = groupe_matiere_evalue_repository
        self.bareme_repository = bareme_repository
        self.appreciation_repository = appreciation_repository
        self.inscription_repository = inscription_repository
        self.annee_repository = annee_repository
        self.depends_evaluation_repository = depends_evaluation_repository

    def _session(self):
        return self.notation_repository.session

    def _get_annee_service(self):
        return AnneeService(self.annee_repository)

    def _not_found(self, error_code: str, message: str):
        raise HTTPException(
            status_code=404,
            detail={"error_code": error_code, "message": message},
        )

    def _get_contexte(self, id_evaluation: int, id_classe: int, id_matiere_evalue: int):
        """Vérifie l'évaluation, la classe et la matière évaluée pour l'année en cours.
        Retourne (annee, barème de la matière, ids des élèves inscrits dans la classe)"""
        annee = self._get_annee_service().get_annee_scolaire()[0]
        if self.evaluation_repository.findOne(id_evaluation) is None:
            self._not_found("EVALUATION_NOT_FOUND", "Évaluation non trouvée")
        classe = self.classe_repository.findOne(id_classe)
        if classe is None:
            self._not_found("CLASSE_NOT_FOUND", "Classe non trouvée")
        matiere_evalue = self.matiere_evalue_repository.findOne(id_matiere_evalue)
        if matiere_evalue is None:
            self._not_found("MATIERE_EVALUE_NOT_FOUND", "Matière évaluée non trouvée")
        groupe = self.groupe_matiere_evalue_repository.findOne(matiere_evalue.id_groupe_matiere)
        if groupe is None or groupe.id_niveau != classe.id_niveau:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code": "MATIERE_NIVEAU_DIFFERENT",
                    "message": "La matière évaluée n'appartient pas au niveau de la classe",
                },
            )
        bareme = self.bareme_repository.findOne(matiere_evalue.id_bareme)
        if bareme is None:
            self._not_found("BAREME_NOT_FOUND", "Barème de la matière évaluée non trouvé")
        ids_inscrits = {
            i.id_eleve for i in self.inscription_repository.findBy(
                id_classe=id_classe, id_annee=annee.id, is_inscris=True)
        }
        return annee, bareme, ids_inscrits

    def _get_type_notation(self) -> TypeNotation:
        """Type de notation déduit de type_school (.env) : education_base -> Primaire, secondaire -> Secondaire"""
        type_school = get_settings().type_school.strip().lower()
        type_notation = TYPE_NOTATION_PAR_TYPE_SCHOOL.get(type_school)
        if type_notation is None:
            raise HTTPException(
                status_code=500,
                detail={
                    "error_code": "TYPE_SCHOOL_INVALIDE",
                    "message": f"Valeur de type_school invalide dans la configuration : {get_settings().type_school}",
                },
            )
        return type_notation

    def _get_dependances(self, id_evaluation: int):
        return self.depends_evaluation_repository.findBy(id_evaluation=id_evaluation)

    def _check_saisie_manuelle(self, id_evaluation: int):
        """Les notes d'une évaluation qui a des dépendances sont calculées, jamais saisies"""
        if len(self._get_dependances(id_evaluation)) > 0:
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "EVALUATION_CALCULEE",
                    "message": "Les notes de cette évaluation sont calculées à partir de ses dépendances : utilisez le calcul automatique",
                },
            )

    def _check_eleves(self, notes: list[NotationItemDTO], ids_inscrits: set[int]):
        ids_eleves = [n.id_eleve for n in notes]
        if len(ids_eleves) != len(set(ids_eleves)):
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "DUPLICATION_ELEVE_IN_REQUEST",
                    "message": "Des élèves dupliqués sont présents dans la liste",
                },
            )
        for id_eleve in ids_eleves:
            if id_eleve not in ids_inscrits:
                self._not_found(
                    "ELEVE_NON_INSCRIT",
                    f"L'élève {id_eleve} n'est pas inscrit dans cette classe pour l'année en cours",
                )

    def _get_id_appreciation(self, item: NotationItemDTO, bareme: Bareme) -> int:
        """Vérifie que la note respecte le barème et retourne l'appréciation correspondante"""
        if item.note < 0 or item.note > bareme.valeur_max:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code": "NOTE_HORS_BAREME",
                    "message": f"La note {item.note} de l'élève {item.id_eleve} doit être comprise entre 0 et {bareme.valeur_max} (barème {bareme.libelle})",
                },
            )
        appreciations = self.appreciation_repository.find_chevauchement(bareme.id, item.note, item.note)
        if len(appreciations) == 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code": "APPRECIATION_INTROUVABLE",
                    "message": f"Aucune appréciation du barème {bareme.libelle} ne couvre la note {item.note}",
                },
            )
        return appreciations[0].id

    def _get_notations_contexte(self, id_evaluation: int, id_classe: int, id_matiere_evalue: int, id_annee: int, load_relations: bool = False):
        return self.notation_repository.findBy(
            load_relations=load_relations,
            id_evaluation=id_evaluation, id_classe=id_classe,
            id_matiere_evalue=id_matiere_evalue, id_annee=id_annee,
        )

    def add_bulk_notations(self, data: NotationBulkCreateDTO):
        """Enregistre en masse les notes des élèves d'une classe pour une évaluation et une matière évaluée
        pendant l'année en cours"""
        try:
            annee, bareme, ids_inscrits = self._get_contexte(
                data.id_evaluation, data.id_classe, data.id_matiere_evalue)
            self._check_saisie_manuelle(data.id_evaluation)
            self._check_eleves(data.notes, ids_inscrits)

            deja_notes = {
                n.id_eleve for n in self._get_notations_contexte(
                    data.id_evaluation, data.id_classe, data.id_matiere_evalue, annee.id)
            }
            data_list = []
            for item in data.notes:
                if item.id_eleve in deja_notes:
                    raise HTTPException(
                        status_code=409,
                        detail={
                            "error_code": "DUPLICATION_NOTATION",
                            "message": f"L'élève {item.id_eleve} a déjà une note pour cette évaluation et cette matière",
                        },
                    )
                data_list.append({
                    "note": item.note,
                    "type": self._get_type_notation().value,
                    "id_eleve": item.id_eleve,
                    "id_evaluation": data.id_evaluation,
                    "id_classe": data.id_classe,
                    "id_matiere_evalue": data.id_matiere_evalue,
                    "id_annee": annee.id,
                    "id_appreciation": self._get_id_appreciation(item, bareme),
                })

            self.notation_repository.InsertMany(data_list)
            self._recalculer_parents(
                data.id_evaluation, data.id_classe, data.id_matiere_evalue, annee, bareme, ids_inscrits)
            self._session().commit()
            ids_eleves = {item.id_eleve for item in data.notes}
            return [
                n for n in self._get_notations_contexte(
                    data.id_evaluation, data.id_classe, data.id_matiere_evalue, annee.id, load_relations=True)
                if n.id_eleve in ids_eleves
            ]
        except HTTPException as http_exec:
            self._session().rollback()
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'enregistrement des notes: {str(e)}")

    def update_bulk_notations(self, data: NotationBulkUpdateDTO):
        """Modifie en masse les notes des élèves d'une classe pour une évaluation et une matière évaluée
        pendant l'année en cours"""
        try:
            annee, bareme, ids_inscrits = self._get_contexte(
                data.id_evaluation, data.id_classe, data.id_matiere_evalue)
            self._check_saisie_manuelle(data.id_evaluation)
            self._check_eleves(data.notes, ids_inscrits)

            existantes = {
                n.id_eleve: n for n in self._get_notations_contexte(
                    data.id_evaluation, data.id_classe, data.id_matiere_evalue, annee.id)
            }
            for item in data.notes:
                db_notation = existantes.get(item.id_eleve)
                if db_notation is None:
                    self._not_found(
                        "NOTATION_NOT_FOUND",
                        f"L'élève {item.id_eleve} n'a pas encore de note pour cette évaluation et cette matière",
                    )
                db_notation.note = item.note
                db_notation.id_appreciation = self._get_id_appreciation(item, bareme)
                self.notation_repository.save(db_notation)

            self._recalculer_parents(
                data.id_evaluation, data.id_classe, data.id_matiere_evalue, annee, bareme, ids_inscrits)
            self._session().commit()
            ids_eleves = {item.id_eleve for item in data.notes}
            return [
                n for n in self._get_notations_contexte(
                    data.id_evaluation, data.id_classe, data.id_matiere_evalue, annee.id, load_relations=True)
                if n.id_eleve in ids_eleves
            ]
        except HTTPException as http_exec:
            self._session().rollback()
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification des notes: {str(e)}")

    def get_notations(self, id_evaluation: int, id_classe: int, id_matiere_evalue: int):
        """Récupère les notes des élèves d'une classe pour une évaluation et une matière évaluée
        pendant l'année en cours"""
        try:
            annee, _, _ = self._get_contexte(id_evaluation, id_classe, id_matiere_evalue)
            return self._get_notations_contexte(
                id_evaluation, id_classe, id_matiere_evalue, annee.id, load_relations=True)
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la récupération des notes: {str(e)}")

    def _calculer(self, id_evaluation: int, id_classe: int, id_matiere_evalue: int, annee, bareme, ids_inscrits: set[int]):
        """Calcule et enregistre (sans commit) les notes d'une évaluation qui a des dépendances.
        note = somme(note x pourcentage) / somme(pourcentages), sur les seules dépendances
        où l'élève a une note (non classé dans une dépendance = dépendance ignorée, pas un 0).
        Retourne (ids des élèves calculés, ids des élèves non classés)"""
        dependances = self._get_dependances(id_evaluation)
        if len(dependances) == 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code": "EVALUATION_SANS_DEPENDANCE",
                    "message": "Cette évaluation n'a pas de dépendances : ses notes se saisissent manuellement",
                },
            )
        total_pourcentage = round(sum(d.pourcentage for d in dependances), 2)
        if total_pourcentage != 100:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code": "POURCENTAGE_INCOMPLET",
                    "message": f"La somme des pourcentages des dépendances est de {total_pourcentage}% : elle doit être de 100% pour calculer les notes",
                },
            )

        # Notes de chaque dépendance par élève : {id_dependance: {id_eleve: note}}
        notes_dependances = {
            d.id_dependance: {
                n.id_eleve: n.note for n in self._get_notations_contexte(
                    d.id_dependance, id_classe, id_matiere_evalue, annee.id)
            }
            for d in dependances
        }
        existantes = {
            n.id_eleve: n for n in self._get_notations_contexte(
                id_evaluation, id_classe, id_matiere_evalue, annee.id)
        }

        eleves_non_classes = []
        ids_calcules = set()
        for id_eleve in sorted(ids_inscrits):
            # Un élève sans note dans une dépendance y est non classé (ce n'est pas un 0) :
            # la note est calculée uniquement à partir des dépendances où il a une note,
            # en ramenant leurs pourcentages sur 100
            dependances_notees = [
                d for d in dependances if id_eleve in notes_dependances[d.id_dependance]
            ]
            if len(dependances_notees) == 0:
                eleves_non_classes.append(id_eleve)
                # Note calculée lors d'un précédent calcul devenue sans fondement
                if id_eleve in existantes:
                    self.notation_repository.deleteOne(existantes[id_eleve].id)
                continue
            pourcentage_note = sum(d.pourcentage for d in dependances_notees)
            note = arrondir_note_calculee(sum(
                notes_dependances[d.id_dependance][id_eleve] * d.pourcentage
                for d in dependances_notees
            ) / pourcentage_note)
            id_appreciation = self._get_id_appreciation(
                NotationItemDTO(id_eleve=id_eleve, note=note), bareme)
            db_notation = existantes.get(id_eleve)
            if db_notation is None:
                db_notation = Notation(
                    note=note,
                    type=self._get_type_notation().value,
                    id_eleve=id_eleve,
                    id_evaluation=id_evaluation,
                    id_classe=id_classe,
                    id_matiere_evalue=id_matiere_evalue,
                    id_annee=annee.id,
                    id_appreciation=id_appreciation,
                )
            else:
                db_notation.note = note
                db_notation.id_appreciation = id_appreciation
            self.notation_repository.save(db_notation)
            ids_calcules.add(id_eleve)
        return ids_calcules, eleves_non_classes

    def _recalculer_parents(self, id_evaluation: int, id_classe: int, id_matiere_evalue: int, annee, bareme, ids_inscrits: set[int]):
        """Après une saisie ou une modification des notes d'une dépendance : recalcule (sans commit)
        les notes des évaluations parentes qui en avaient déjà sur cette classe et cette matière,
        puis celles de leurs propres parents (cascade)"""
        for lien in self.depends_evaluation_repository.findBy(id_dependance=id_evaluation):
            id_parent = lien.id_evaluation
            if self._get_notations_contexte(id_parent, id_classe, id_matiere_evalue, annee.id):
                self._calculer(id_parent, id_classe, id_matiere_evalue, annee, bareme, ids_inscrits)
                self._recalculer_parents(id_parent, id_classe, id_matiere_evalue, annee, bareme, ids_inscrits)

    def calculer_notations(self, id_evaluation: int, id_classe: int, id_matiere_evalue: int):
        """Calcule et enregistre les notes d'une évaluation qui a des dépendances, pour une classe
        et une matière évaluée pendant l'année en cours (puis recalcule ses parents déjà notés)"""
        try:
            annee, bareme, ids_inscrits = self._get_contexte(id_evaluation, id_classe, id_matiere_evalue)
            ids_calcules, eleves_non_classes = self._calculer(
                id_evaluation, id_classe, id_matiere_evalue, annee, bareme, ids_inscrits)
            self._recalculer_parents(id_evaluation, id_classe, id_matiere_evalue, annee, bareme, ids_inscrits)
            self._session().commit()
            notations = [
                n for n in self._get_notations_contexte(
                    id_evaluation, id_classe, id_matiere_evalue, annee.id, load_relations=True)
                if n.id_eleve in ids_calcules
            ]
            return {"notations": notations, "eleves_non_classes": eleves_non_classes}
        except HTTPException as http_exec:
            self._session().rollback()
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors du calcul des notes: {str(e)}")
