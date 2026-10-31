from datetime import datetime

from fastapi import HTTPException

from models.evaluations.discipline_eleve import DisciplineEleve
from models.evaluations.evaluation import Evaluation
from repositories.administration.annee_repository import AnneeRepository
from repositories.administration.configuration_repository import ConfigurationRepository
from repositories.administration.discipline_decision_repository import DisciplineDecisionRepository
from repositories.enseignement.presence_eleve_repository import PresenceEleveRepository
from repositories.evaluations.discipline_eleve_repository import DisciplineEleveRepository
from repositories.evaluations.evaluation_repository import EvaluationRepository
from repositories.inscription.inscription_repository import InscriptionRepository
from schemas.evaluations.discipline_eleve_dto import (
    DisciplineEleveBase,
    DisciplineEleveBulkCreateDTO,
    DisciplineEleveBulkUpdateDTO,
    DisciplineEleveCreateDTO,
    DisciplineEleveUpdateDTO,
)
from services.administration.annee_service import AnneeService


class DisciplineEleveService:
    def __init__(
        self,
        discipline_repository: DisciplineEleveRepository,
        evaluation_repository: EvaluationRepository,
        inscription_repository: InscriptionRepository,
        presence_eleve_repository: PresenceEleveRepository,
        configuration_repository: ConfigurationRepository,
        annee_repository: AnneeRepository,
        discipline_decision_repository: DisciplineDecisionRepository,
    ):
        self.discipline_repository = discipline_repository
        self.evaluation_repository = evaluation_repository
        self.inscription_repository = inscription_repository
        self.presence_eleve_repository = presence_eleve_repository
        self.configuration_repository = configuration_repository
        self.annee_repository = annee_repository
        self.discipline_decision_repository = discipline_decision_repository

    def _session(self):
        return self.discipline_repository.session

    def _get_id_decision(self, nb_heure_non_justifie: int) -> int | None:
        """Retourne l'id de la décision disciplinaire dont l'intervalle contient le nombre d'heures
        d'absence NON justifiées (nb_heure_obtenu) ; None si aucune décision ne correspond"""
        decisions = self.discipline_decision_repository.find_chevauchement(
            nb_heure_non_justifie, nb_heure_non_justifie)
        return decisions[0].id if decisions else None

    def _get_annee_service(self):
        return AnneeService(self.annee_repository)

    def _is_appel_actif(self) -> bool:
        configurations = self.configuration_repository.findAll()
        return len(configurations) > 0 and configurations[0].is_appel

    def _check_discipline_geree(self):
        if not self.configuration_repository.is_discipline_geree():
            raise HTTPException(
                status_code=403,
                detail={
                    "error_code": "DISCIPLINE_NON_GEREE",
                    "message": "La discipline n'est pas gérée par l'établissement (configuration)",
                },
            )

    def _check_appel_inactif(self):
        self._check_discipline_geree()
        if self._is_appel_actif():
            raise HTTPException(
                status_code=403,
                detail={
                    "error_code": "APPEL_ACTIVE",
                    "message": "L'appel est activé : les disciplines doivent être calculées automatiquement à partir des présences",
                },
            )

    def _check_appel_actif(self):
        self._check_discipline_geree()
        if not self._is_appel_actif():
            raise HTTPException(
                status_code=403,
                detail={
                    "error_code": "APPEL_NOT_ACTIVE",
                    "message": "L'appel n'est pas activé dans la configuration : le calcul automatique est impossible",
                },
            )

    def _get_evaluation(self, id_evaluation: int) -> Evaluation:
        db_evaluation = self.evaluation_repository.findOne(id_evaluation, load_relations=False)
        if db_evaluation is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "EVALUATION_NOT_FOUND",
                    "message": "Évaluation non trouvée",
                },
            )
        return db_evaluation

    def _check_eleve_inscrit(self, id_eleve: int, id_classe: int, id_annee: int):
        inscriptions = self.inscription_repository.findBy(
            load_relations=False,
            id_eleve=id_eleve, id_classe=id_classe, id_annee=id_annee, is_inscris=True,
        )
        if len(inscriptions) == 0:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "ELEVE_NON_INSCRIT",
                    "message": f"L'élève {id_eleve} n'est pas inscrit dans cette classe pour l'année en cours",
                },
            )

    def _check_total(self, discipline: DisciplineEleveBase):
        if discipline.nb_heure_total != discipline.nb_heure_obtenu + discipline.nb_heure_justifie:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code": "TOTAL_INCOHERENT",
                    "message": "Le nombre total d'heures doit être égal à la somme des heures obtenues et justifiées",
                },
            )

    def _check_discipline_exists(self, db_discipline: DisciplineEleve | None):
        if db_discipline is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "DISCIPLINE_NOT_FOUND",
                    "message": "Discipline de l'élève non trouvée",
                },
            )

    def _appliquer_modification(self, db_discipline: DisciplineEleve, discipline_update: DisciplineEleveUpdateDTO):
        """Applique les champs modifiés sur la discipline après avoir vérifié la cohérence du total"""
        update_data = discipline_update.model_dump(
            exclude_unset=True, exclude_none=True, exclude={"id"})
        nouvelle = DisciplineEleveBase(
            nb_heure_obtenu=update_data.get("nb_heure_obtenu", db_discipline.nb_heure_obtenu),
            nb_heure_justifie=update_data.get("nb_heure_justifie", db_discipline.nb_heure_justifie),
            nb_heure_total=update_data.get("nb_heure_total", db_discipline.nb_heure_total),
        )
        self._check_total(nouvelle)
        for key, value in update_data.items():
            setattr(db_discipline, key, value)
        db_discipline.id_discipline_decision = self._get_id_decision(db_discipline.nb_heure_obtenu)
        return self.discipline_repository.save(db_discipline)

    def _check_discipline_not_exists(self, id_eleve: int, id_annee: int, id_classe: int, id_evaluation: int):
        exist = self.discipline_repository.findBy(
            load_relations=False,
            id_eleve=id_eleve, id_annee=id_annee, id_classe=id_classe, id_evaluation=id_evaluation,
        )
        if len(exist) > 0:
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "DUPLICATION_DISCIPLINE",
                    "message": f"La discipline de l'élève {id_eleve} existe déjà pour cette évaluation",
                },
            )

    def add_discipline(self, discipline_in: DisciplineEleveCreateDTO, id_eleve: int, id_classe: int, id_evaluation: int):
        """Ajoute manuellement la discipline d'un élève pour une évaluation (uniquement si l'appel est désactivé)"""
        try:
            self._check_appel_inactif()
            annee = self._get_annee_service().get_annee_scolaire()[0]
            self._get_evaluation(id_evaluation)
            self._check_eleve_inscrit(id_eleve, id_classe, annee.id)
            self._check_total(discipline_in)
            self._check_discipline_not_exists(id_eleve, annee.id, id_classe, id_evaluation)
            discipline_dict = discipline_in.model_dump()
            discipline_dict["id_eleve"] = id_eleve
            discipline_dict["id_classe"] = id_classe
            discipline_dict["id_evaluation"] = id_evaluation
            discipline_dict["id_annee"] = annee.id
            discipline_dict["id_discipline_decision"] = self._get_id_decision(discipline_in.nb_heure_obtenu)
            db_discipline = DisciplineEleve.model_validate(discipline_dict)
            new_discipline = self.discipline_repository.save(db_discipline)
            self._session().commit()
            return new_discipline
        except HTTPException as http_exec:
            self._session().rollback()
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'ajout de la discipline: {str(e)}")

    def add_bulk_disciplines(self, data: DisciplineEleveBulkCreateDTO):
        """Ajoute manuellement en masse les disciplines des élèves d'une classe pour une évaluation
        (uniquement si l'appel est désactivé)"""
        try:
            self._check_appel_inactif()
            annee = self._get_annee_service().get_annee_scolaire()[0]
            self._get_evaluation(data.id_evaluation)
            ids_eleves = [d.id_eleve for d in data.disciplines]
            if len(ids_eleves) != len(set(ids_eleves)):
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error_code": "DUPLICATION_ELEVE_IN_REQUEST",
                        "message": "Des élèves dupliqués sont présents dans la liste",
                    },
                )
            for discipline in data.disciplines:
                self._check_eleve_inscrit(discipline.id_eleve, data.id_classe, annee.id)
                self._check_total(discipline)
                self._check_discipline_not_exists(
                    discipline.id_eleve, annee.id, data.id_classe, data.id_evaluation)

            data_list = [
                {
                    **d.model_dump(),
                    "id_classe": data.id_classe,
                    "id_evaluation": data.id_evaluation,
                    "id_annee": annee.id,
                    "id_discipline_decision": self._get_id_decision(d.nb_heure_obtenu),
                }
                for d in data.disciplines
            ]
            self.discipline_repository.InsertMany(data_list)
            self._session().commit()
            return [
                d for d in self.discipline_repository.findBy(
                    load_relations=False,
                    id_classe=data.id_classe, id_evaluation=data.id_evaluation, id_annee=annee.id,
                )
                if d.id_eleve in ids_eleves
            ]
        except HTTPException as http_exec:
            self._session().rollback()
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'ajout en masse des disciplines: {str(e)}")

    def update_discipline(self, discipline_id: int, discipline_update: DisciplineEleveUpdateDTO):
        """Modifie manuellement la discipline d'un élève (uniquement si l'appel est désactivé)"""
        try:
            self._check_appel_inactif()
            db_discipline = self.discipline_repository.findOne(discipline_id, load_relations=False)
            self._check_discipline_exists(db_discipline)
            updated = self._appliquer_modification(db_discipline, discipline_update)
            self._session().commit()
            return updated
        except HTTPException as http_exec:
            self._session().rollback()
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification de la discipline: {str(e)}")

    def update_bulk_disciplines(self, data: DisciplineEleveBulkUpdateDTO):
        """Modifie manuellement en masse les disciplines des élèves (uniquement si l'appel est désactivé)"""
        try:
            self._check_appel_inactif()
            ids = [d.id for d in data.disciplines]
            if len(ids) != len(set(ids)):
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error_code": "DUPLICATION_DISCIPLINE_IN_REQUEST",
                        "message": "Des disciplines dupliquées sont présentes dans la liste",
                    },
                )
            resultats = []
            for item in data.disciplines:
                db_discipline = self.discipline_repository.findOne(item.id, load_relations=False)
                self._check_discipline_exists(db_discipline)
                resultats.append(self._appliquer_modification(db_discipline, item))
            self._session().commit()
            return resultats
        except HTTPException as http_exec:
            self._session().rollback()
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification en masse des disciplines: {str(e)}")

    def _calculer_et_enregistrer(self, ids_eleves: list[int], id_classe: int, id_annee: int, db_evaluation: Evaluation):
        """Calcule les heures d'absence des élèves sur la période de l'évaluation à partir des présences
        et des heures de cours, puis crée ou met à jour leur discipline"""
        # Minutes d'absence par élève : {id_eleve: [non_justifiees, justifiees]}
        minutes = {id_eleve: [0, 0] for id_eleve in ids_eleves}
        id_eleve_filtre = ids_eleves[0] if len(ids_eleves) == 1 else None
        absences = self.presence_eleve_repository.find_absences(
            id_classe, id_annee, db_evaluation.date_deb, db_evaluation.date_fin, id_eleve_filtre)
        for id_eleve, is_justifie, heure_deb, heure_fin in absences:
            if id_eleve not in minutes:
                continue
            duree = datetime.combine(datetime.min, heure_fin) - datetime.combine(datetime.min, heure_deb)
            minutes[id_eleve][1 if is_justifie else 0] += int(duree.total_seconds() // 60)

        existantes = {
            d.id_eleve: d
            for d in self.discipline_repository.findBy(
                load_relations=False,
                id_classe=id_classe, id_annee=id_annee, id_evaluation=db_evaluation.id,
            )
        }
        resultats = []
        for id_eleve, (min_non_justifie, min_justifie) in minutes.items():
            nb_heure_obtenu = round(min_non_justifie / 60)
            nb_heure_justifie = round(min_justifie / 60)
            nb_heure_total = nb_heure_obtenu + nb_heure_justifie
            valeurs = {
                "nb_heure_obtenu": nb_heure_obtenu,
                "nb_heure_justifie": nb_heure_justifie,
                "nb_heure_total": nb_heure_total,
                "id_discipline_decision": self._get_id_decision(nb_heure_obtenu),
            }
            db_discipline = existantes.get(id_eleve)
            if db_discipline is None:
                db_discipline = DisciplineEleve.model_validate({
                    **valeurs,
                    "id_eleve": id_eleve,
                    "id_classe": id_classe,
                    "id_annee": id_annee,
                    "id_evaluation": db_evaluation.id,
                })
            else:
                for key, value in valeurs.items():
                    setattr(db_discipline, key, value)
            resultats.append(self.discipline_repository.save(db_discipline))
        return resultats

    def calculer_discipline_eleve(self, id_eleve: int, id_classe: int, id_evaluation: int):
        """Calcule et enregistre automatiquement la discipline d'un élève pour une évaluation
        (uniquement si l'appel est activé)"""
        try:
            self._check_appel_actif()
            annee = self._get_annee_service().get_annee_scolaire()[0]
            db_evaluation = self._get_evaluation(id_evaluation)
            self._check_eleve_inscrit(id_eleve, id_classe, annee.id)
            resultat = self._calculer_et_enregistrer([id_eleve], id_classe, annee.id, db_evaluation)[0]
            self._session().commit()
            return resultat
        except HTTPException as http_exec:
            self._session().rollback()
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors du calcul de la discipline de l'élève: {str(e)}")

    def calculer_disciplines_classe(self, id_classe: int, id_evaluation: int):
        """Calcule et enregistre automatiquement la discipline de tous les élèves inscrits
        dans une classe pour une évaluation (uniquement si l'appel est activé)"""
        try:
            self._check_appel_actif()
            annee = self._get_annee_service().get_annee_scolaire()[0]
            db_evaluation = self._get_evaluation(id_evaluation)
            inscriptions = self.inscription_repository.findBy(
                load_relations=False, id_classe=id_classe, id_annee=annee.id, is_inscris=True)
            if len(inscriptions) == 0:
                return []
            ids_eleves = [i.id_eleve for i in inscriptions]
            resultats = self._calculer_et_enregistrer(ids_eleves, id_classe, annee.id, db_evaluation)
            self._session().commit()
            return resultats
        except HTTPException as http_exec:
            self._session().rollback()
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors du calcul des disciplines de la classe: {str(e)}")
