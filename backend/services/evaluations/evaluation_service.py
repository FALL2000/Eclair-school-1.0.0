from datetime import date

from fastapi import HTTPException

from models.evaluations.depends_evaluation import DependsEvaluation
from models.evaluations.evaluation import Evaluation
from repositories.administration.trimestre_repository import TrimestreRepository
from repositories.evaluations.depends_evaluation_repository import DependsEvaluationRepository
from repositories.evaluations.evaluation_repository import EvaluationRepository
from schemas.evaluations.depends_evaluation_dto import (
    DependsEvaluationBulkCreateDTO,
    DependsEvaluationUpdateDTO,
)
from schemas.evaluations.evaluation_dto import EvaluationCreateDTO, EvaluationUpdateDTO


class EvaluationService:
    def __init__(
        self,
        evaluation_repository: EvaluationRepository,
        trimestre_repository: TrimestreRepository,
        depends_evaluation_repository: DependsEvaluationRepository,
    ):
        self.evaluation_repository = evaluation_repository
        self.trimestre_repository = trimestre_repository
        self.depends_evaluation_repository = depends_evaluation_repository

    def _session(self):
        return self.evaluation_repository.session

    def _check_code_exists(self, code: str):
        exist_evaluation = self.evaluation_repository.findByCode(code)
        if len(exist_evaluation) > 0:
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "DUPLICATION_CODE",
                    "message": f"L'évaluation avec le code {code} existe déjà."
                }
            )

    def _check_evaluation_exists(self, db_evaluation: Evaluation | None):
        if db_evaluation is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "EVALUATION_NOT_FOUND",
                    "message": "Évaluation non trouvée"
                }
            )

    def _check_dependance_exists(self, db_dependance: DependsEvaluation | None):
        if db_dependance is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "DEPENDANCE_NOT_FOUND",
                    "message": "Dépendance non trouvée"
                }
            )

    def _check_parent_sans_notations(self, id_parent: int, error_code: str, message: str):
        """Lève une erreur 409 si l'évaluation parente a déjà des notations"""
        db_parent = self.evaluation_repository.findOne(id_parent, load_relations=True)
        if db_parent is not None and len(db_parent.notations) > 0:
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": error_code,
                    "message": message
                }
            )

    def _check_trimestre_exists(self, id_trimestre: int):
        if self.trimestre_repository.findOne(id_trimestre, load_relations=False) is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "TRIMESTRE_NOT_FOUND",
                    "message": "Trimestre non trouvé"
                }
            )

    def _check_dates(self, date_deb: date, date_fin: date):
        if date_deb > date_fin:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code": "INVALID_DATES",
                    "message": "La date de début doit être antérieure ou égale à la date de fin"
                }
            )

    def add_evaluation(self, evaluation_in: EvaluationCreateDTO, id_trimestre: int):
        """Ajoute une évaluation en BD"""
        try:
            self._check_trimestre_exists(id_trimestre)
            self._check_code_exists(evaluation_in.code)
            self._check_dates(evaluation_in.date_deb, evaluation_in.date_fin)
            evaluation_dict = evaluation_in.model_dump()
            evaluation_dict["id_trimestre"] = id_trimestre
            db_evaluation = Evaluation.model_validate(evaluation_dict)
            new_evaluation = self.evaluation_repository.save(db_evaluation)
            self._session().commit()
            return new_evaluation
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'ajout de l'évaluation: {str(e)}")

    def _check_coherence_dependances(self, evaluation_id: int, id_trimestre: int, date_deb: date, date_fin: date):
        """Vérifie que le nouveau trimestre et la nouvelle période d'une évaluation restent cohérents
        avec ses dépendances (si elle est parente) et avec ses parents (si elle est une dépendance)"""
        # L'évaluation est parente : chaque dépendance doit rester dans son trimestre et sa période
        liens_dependances = self.depends_evaluation_repository.findBy(
            load_relations=False, id_evaluation=evaluation_id)
        for lien in liens_dependances:
            db_dependance = self.evaluation_repository.findOne(
                lien.id_dependance, load_relations=False)
            if db_dependance.id_trimestre != id_trimestre:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error_code": "TRIMESTRE_DIFFERENT",
                        "message": f"L'évaluation dépendante {db_dependance.code} n'appartient pas au nouveau trimestre de l'évaluation"
                    }
                )
            if db_dependance.date_deb < date_deb or db_dependance.date_fin > date_fin:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error_code": "PERIODE_HORS_INTERVALLE",
                        "message": (
                            f"La nouvelle période ({date_deb:%d/%m/%Y} - {date_fin:%d/%m/%Y}) doit contenir "
                            f"celle de l'évaluation dépendante {db_dependance.code} "
                            f"({db_dependance.date_deb:%d/%m/%Y} - {db_dependance.date_fin:%d/%m/%Y})"
                        )
                    }
                )

        # L'évaluation est une dépendance : elle doit rester dans le trimestre et la période de chaque parent
        liens_parents = self.depends_evaluation_repository.findBy(
            load_relations=False, id_dependance=evaluation_id)
        for lien in liens_parents:
            db_parent = self.evaluation_repository.findOne(
                lien.id_evaluation, load_relations=False)
            if db_parent.id_trimestre != id_trimestre:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error_code": "TRIMESTRE_DIFFERENT",
                        "message": f"Le nouveau trimestre ne correspond pas à celui de l'évaluation parente {db_parent.code}"
                    }
                )
            if date_deb < db_parent.date_deb or date_fin > db_parent.date_fin:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error_code": "PERIODE_HORS_INTERVALLE",
                        "message": (
                            f"La nouvelle période ({date_deb:%d/%m/%Y} - {date_fin:%d/%m/%Y}) doit être comprise "
                            f"dans celle de l'évaluation parente {db_parent.code} "
                            f"({db_parent.date_deb:%d/%m/%Y} - {db_parent.date_fin:%d/%m/%Y})"
                        )
                    }
                )

    def update_evaluation(self, evaluation_id: int, evaluation_update: EvaluationUpdateDTO):
        """Modifie une évaluation en BD"""
        try:
            db_evaluation = self.evaluation_repository.findOne(evaluation_id)
            self._check_evaluation_exists(db_evaluation)
            if evaluation_update.code is not None and evaluation_update.code != db_evaluation.code:
                self._check_code_exists(evaluation_update.code)
            if evaluation_update.id_trimestre is not None and evaluation_update.id_trimestre != db_evaluation.id_trimestre:
                self._check_trimestre_exists(evaluation_update.id_trimestre)
            new_id_trimestre = evaluation_update.id_trimestre or db_evaluation.id_trimestre
            new_date_deb = evaluation_update.date_deb or db_evaluation.date_deb
            new_date_fin = evaluation_update.date_fin or db_evaluation.date_fin
            self._check_dates(new_date_deb, new_date_fin)
            if (
                new_id_trimestre != db_evaluation.id_trimestre
                or new_date_deb != db_evaluation.date_deb
                or new_date_fin != db_evaluation.date_fin
            ):
                self._check_coherence_dependances(
                    evaluation_id, new_id_trimestre, new_date_deb, new_date_fin)
            update_data = evaluation_update.model_dump(exclude_unset=True, exclude_none=True)
            for key, value in update_data.items():
                setattr(db_evaluation, key, value)
            updated = self.evaluation_repository.save(db_evaluation)
            self._session().commit()
            return updated
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification de l'évaluation: {str(e)}")

    def delete_evaluation(self, evaluation_id: int):
        """Supprime une évaluation en BD — impossible si des notes ou disciplines y sont rattachées"""
        try:
            db_evaluation = self.evaluation_repository.findOne(evaluation_id, load_relations=True)
            self._check_evaluation_exists(db_evaluation)
            if len(db_evaluation.notations) > 0 or len(db_evaluation.disciplines) > 0:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error_code": "CANNOT_DELETE",
                        "message": "Impossible de supprimer une évaluation à laquelle des notes ou disciplines sont rattachées"
                    }
                )
            # La suppression retire aussi les liens vers ses parents : interdit si un parent a déjà des notes
            for lien in db_evaluation.dependants:
                self._check_parent_sans_notations(
                    lien.id_evaluation,
                    "CANNOT_DELETE",
                    "Impossible de supprimer une évaluation dont dépend une évaluation qui a déjà des notations",
                )
            deleted = self.evaluation_repository.deleteOne(evaluation_id)
            if deleted:
                self._session().commit()
                return {
                    "success": True,
                    "detail": {"id": evaluation_id, "message": "Évaluation supprimée"}
                }
            return {
                "success": False,
                "detail": {"id": evaluation_id, "message": "Évaluation non supprimée"}
            }
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la suppression de l'évaluation: {str(e)}")

    def get_one_evaluation(self, evaluation_id: int):
        """Récupère une évaluation en BD"""
        try:
            db_evaluation = self.evaluation_repository.findOne(evaluation_id)
            self._check_evaluation_exists(db_evaluation)
            return db_evaluation
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la récupération de l'évaluation: {str(e)}")

    def get_all_evaluations(self, id_trimestre: int | None = None):
        """Récupère toutes les évaluations en BD, éventuellement filtrées par trimestre"""
        try:
            if id_trimestre is not None:
                return self.evaluation_repository.findBy(load_relations=False, id_trimestre=id_trimestre)
            return self.evaluation_repository.findAll(load_relations=False)
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la récupération des évaluations: {str(e)}")

    def _creerait_cycle(self, id_evaluation: int, id_dependance: int) -> bool:
        """Vérifie si id_evaluation est atteignable depuis id_dependance via les dépendances existantes.
        Si c'est le cas, ajouter la dépendance id_evaluation -> id_dependance créerait un cycle."""
        a_visiter = [id_dependance]
        visites = set()
        while a_visiter:
            courant = a_visiter.pop()
            if courant == id_evaluation:
                return True
            if courant in visites:
                continue
            visites.add(courant)
            liens = self.depends_evaluation_repository.findBy(
                load_relations=False, id_evaluation=courant)
            a_visiter.extend(lien.id_dependance for lien in liens)
        return False

    def add_dependances(self, evaluation_id: int, data: DependsEvaluationBulkCreateDTO):
        """Ajoute des dépendances à une évaluation en BD"""
        try:
            db_evaluation = self.evaluation_repository.findOne(evaluation_id, load_relations=True)
            self._check_evaluation_exists(db_evaluation)
            if len(db_evaluation.notations) > 0:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error_code": "CANNOT_ADD_DEPENDANCE",
                        "message": "Impossible d'ajouter des dépendances à une évaluation qui a déjà des notations"
                    }
                )

            ids_dependances = [d.id_dependance for d in data.dependances]
            if len(ids_dependances) != len(set(ids_dependances)):
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error_code": "DUPLICATION_DEPENDANCE_IN_REQUEST",
                        "message": "Des dépendances dupliquées sont présentes dans la liste"
                    }
                )

            existantes = self.depends_evaluation_repository.findBy(
                load_relations=False, id_evaluation=evaluation_id)
            ids_existants = {d.id_dependance for d in existantes}

            for dependance in data.dependances:
                if dependance.id_dependance == evaluation_id:
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "error_code": "AUTO_DEPENDANCE",
                            "message": "Une évaluation ne peut pas dépendre d'elle-même"
                        }
                    )
                db_dependance = self.evaluation_repository.findOne(
                    dependance.id_dependance, load_relations=False)
                if db_dependance is None:
                    raise HTTPException(
                        status_code=404,
                        detail={
                            "error_code": "EVALUATION_DEPENDANCE_NOT_FOUND",
                            "message": f"L'évaluation dépendante {dependance.id_dependance} n'existe pas"
                        }
                    )
                if db_dependance.id_trimestre != db_evaluation.id_trimestre:
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "error_code": "TRIMESTRE_DIFFERENT",
                            "message": f"L'évaluation dépendante {dependance.id_dependance} n'appartient pas au même trimestre que l'évaluation"
                        }
                    )
                if db_dependance.date_deb < db_evaluation.date_deb or db_dependance.date_fin > db_evaluation.date_fin:
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "error_code": "PERIODE_HORS_INTERVALLE",
                            "message": (
                                f"La période de l'évaluation dépendante {dependance.id_dependance} "
                                f"({db_dependance.date_deb:%d/%m/%Y} - {db_dependance.date_fin:%d/%m/%Y}) "
                                f"doit être comprise dans celle de l'évaluation "
                                f"({db_evaluation.date_deb:%d/%m/%Y} - {db_evaluation.date_fin:%d/%m/%Y})"
                            )
                        }
                    )
                if dependance.id_dependance in ids_existants:
                    raise HTTPException(
                        status_code=409,
                        detail={
                            "error_code": "DUPLICATION_DEPENDANCE",
                            "message": f"L'évaluation dépend déjà de l'évaluation {dependance.id_dependance}"
                        }
                    )
                if self._creerait_cycle(evaluation_id, dependance.id_dependance):
                    raise HTTPException(
                        status_code=409,
                        detail={
                            "error_code": "DEPENDANCE_CIRCULAIRE",
                            "message": f"L'évaluation {dependance.id_dependance} dépend déjà (directement ou indirectement) de cette évaluation"
                        }
                    )

            total = sum(d.pourcentage for d in existantes) + \
                sum(d.pourcentage for d in data.dependances)
            if round(total, 2) > 100:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error_code": "POURCENTAGE_DEPASSE",
                        "message": f"La somme des pourcentages des dépendances ({round(total, 2)}%) dépasse 100%"
                    }
                )

            data_list = [
                {**d.model_dump(), "id_evaluation": evaluation_id}
                for d in data.dependances
            ]
            self.depends_evaluation_repository.InsertMany(data_list)
            self._session().commit()
            return self.depends_evaluation_repository.findBy(
                load_relations=False, id_evaluation=evaluation_id)
        except HTTPException as http_exec:
            self._session().rollback()
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'ajout des dépendances: {str(e)}")

    def update_dependance(self, dependance_id: int, dependance_update: DependsEvaluationUpdateDTO):
        """Modifie le pourcentage d'une dépendance en BD"""
        try:
            db_dependance = self.depends_evaluation_repository.findOne(
                dependance_id, load_relations=False)
            self._check_dependance_exists(db_dependance)
            if dependance_update.pourcentage is not None:
                self._check_parent_sans_notations(
                    db_dependance.id_evaluation,
                    "CANNOT_UPDATE",
                    "Impossible de modifier le pourcentage d'une dépendance dont l'évaluation parente a déjà des notations",
                )
                autres = self.depends_evaluation_repository.findBy(
                    load_relations=False, id_evaluation=db_dependance.id_evaluation)
                total = sum(d.pourcentage for d in autres if d.id != dependance_id) + \
                    dependance_update.pourcentage
                if round(total, 2) > 100:
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "error_code": "POURCENTAGE_DEPASSE",
                            "message": f"La somme des pourcentages des dépendances ({round(total, 2)}%) dépasse 100%"
                        }
                    )
                db_dependance.pourcentage = dependance_update.pourcentage
            updated = self.depends_evaluation_repository.save(db_dependance)
            self._session().commit()
            return updated
        except HTTPException as http_exec:
            self._session().rollback()
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification de la dépendance: {str(e)}")

    def delete_dependance(self, dependance_id: int):
        """Supprime une dépendance en BD — impossible si l'évaluation parente a déjà des notations"""
        try:
            db_dependance = self.depends_evaluation_repository.findOne(
                dependance_id, load_relations=False)
            self._check_dependance_exists(db_dependance)
            self._check_parent_sans_notations(
                db_dependance.id_evaluation,
                "CANNOT_DELETE",
                "Impossible de supprimer une dépendance dont l'évaluation parente a déjà des notations",
            )
            deleted = self.depends_evaluation_repository.deleteOne(dependance_id)
            if deleted:
                self._session().commit()
                return {
                    "success": True,
                    "detail": {"id": dependance_id, "message": "Dépendance supprimée"}
                }
            return {
                "success": False,
                "detail": {"id": dependance_id, "message": "Dépendance non supprimée"}
            }
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la suppression de la dépendance: {str(e)}")
