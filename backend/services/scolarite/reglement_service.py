from datetime import date

from fastapi import HTTPException

from common.enumeration import StatutPaiementTranche, StatutReglement
from models.inscription.inscription import Inscription
from models.scolarite.reglement import Reglement
from repositories.administration.annee_repository import AnneeRepository
from repositories.administration.classe_repository import ClasseRepository
from repositories.scolarite.reglement_repository import ReglementRepository
from repositories.scolarite.tranche_pension_repository import TranchePensionRepository
from schemas.scolarite.reglement_dto import (
    PaginatedReglement,
    ReglementCreateDTO,
    ReglementParClasseResponseDTO,
    ReglementResponseDTO,
    ReglementUpdateDTO,
)
from services.administration.annee_service import AnneeService


class ReglementService:
    def __init__(
        self,
        reglement_repository: ReglementRepository,
        annee_repository: AnneeRepository,
        classe_repository: ClasseRepository,
        tranche_pension_repository: TranchePensionRepository,
    ):
        self.reglement_repository = reglement_repository
        self.annee_repository = annee_repository
        self.classe_repository = classe_repository
        self.tranche_pension_repository = tranche_pension_repository

    def _session(self):
        return self.reglement_repository.session

    def _get_annee_service(self):
        return AnneeService(self.annee_repository)

    def _check_reglement_exists(self, db_reglement: Reglement | None):
        if db_reglement is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "REGLEMENT_NOT_FOUND",
                    "message": "Règlement non trouvé",
                },
            )

    def add_reglement(self, reglement_in: ReglementCreateDTO, id_eleve: int, id_tranche_pension: int, current_user: dict):
        """Enregistre un règlement pour l'année scolaire en cours"""
        try:
            annee = self._get_annee_service().get_annee_scolaire()[0]
            reglement_dict = reglement_in.model_dump()
            reglement_dict["id_eleve"] = id_eleve
            reglement_dict["id_tranche_pension"] = id_tranche_pension
            reglement_dict["id_annee"] = annee.id
            reglement_dict["id_user"] = current_user["id"]
            reglement_dict["date_reglement"] = date.today()
            db_reglement = Reglement.model_validate(reglement_dict)
            new_reglement = self.reglement_repository.save(db_reglement)
            self._session().commit()
            self._session().refresh(new_reglement)
            return new_reglement
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'ajout du règlement: {str(e)}")

    def update_reglement(self, reglement_id: int, reglement_update: ReglementUpdateDTO):
        """Modifie un règlement en BD"""
        try:
            db_reglement = self.reglement_repository.findOne(reglement_id, load_relations=True)
            self._check_reglement_exists(db_reglement)
            update_data = reglement_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_reglement, key, value)
            updated = self.reglement_repository.save(db_reglement)
            self._session().commit()
            return updated
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification du règlement: {str(e)}")

    def annuler_reglement(self, reglement_id: int):
        """Annule un règlement (statut annulé)"""
        try:
            db_reglement = self.reglement_repository.findOne(reglement_id, load_relations=True)
            self._check_reglement_exists(db_reglement)
            if db_reglement.statut == StatutReglement.ANNULE:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error_code": "REGLEMENT_DEJA_ANNULE",
                        "message": "Le règlement est déjà annulé",
                    },
                )
            db_reglement.statut = StatutReglement.ANNULE
            updated = self.reglement_repository.save(db_reglement)
            self._session().commit()
            return updated
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'annulation du règlement: {str(e)}")

    def delete_reglement(self, reglement_id: int):
        """Supprime un règlement — impossible durant une année scolaire en cours"""
        try:
            if len(self.annee_repository.findByIs_cloture(False)) > 0:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error_code": "CANNOT_DELETE",
                        "message": "Impossible de supprimer un règlement durant une année scolaire en cours",
                    },
                )
            db_reglement = self.reglement_repository.findOne(reglement_id)
            self._check_reglement_exists(db_reglement)
            deleted = self.reglement_repository.deleteOne(reglement_id)
            if deleted:
                self._session().commit()
                return {"success": True, "detail": {"id": reglement_id, "message": "Règlement supprimé"}}
            return {"success": False, "detail": {"id": reglement_id, "message": "Règlement non supprimé"}}
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la suppression du règlement: {str(e)}")

    def get_all_reglements(self, page: int | None, page_size: int | None) -> PaginatedReglement:
        """Récupère tous les règlements paginés, triés par date décroissante"""
        try:
            total_items = self.reglement_repository.count_all()
            if page_size is None or page is None:
                page_size = total_items if total_items > 0 else 1
                page = 1
            total_pages = (total_items + page_size - 1) // page_size
            if total_pages == 0:
                total_pages = 1
            if page > total_pages:
                page = total_pages
            items = self.reglement_repository.find_all_ordered_desc(
                limit=page_size,
                offset=(page - 1) * page_size,
            ) if page > 0 else []
            return PaginatedReglement(
                page=page,
                page_size=page_size,
                total_items=total_items,
                total_pages=total_pages,
                reglements=items,
            )
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la récupération des règlements: {str(e)}")

    def _get_classe(self, id_classe: int):
        classe = self.classe_repository.findOne(id_classe, load_relations=True)
        if classe is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "CLASSE_NOT_FOUND",
                    "message": "Classe non trouvée",
                },
            )
        return classe

    def _get_reglements_classe(self, classe, id_annee: int, id_tranche_pension: int | None = None) -> list[Reglement]:
        """Récupère les règlements de l'année des élèves inscrits dans une classe,
        éventuellement filtrés par tranche de pension"""
        inscriptions = classe.inscriptions.filter(
            Inscription.id_annee == id_annee, Inscription.is_inscris == True
        ).all()

        reglements = []
        for inscription in inscriptions:
            eleve_reglements = [
                r for r in inscription.eleve.reglements
                if r.id_annee == id_annee
                and (id_tranche_pension is None or r.id_tranche_pension == id_tranche_pension)
            ]
            reglements.extend(eleve_reglements)
        return reglements

    def get_reglements_by_classe(self, id_classe: int) -> list[ReglementParClasseResponseDTO]:
        """Récupère les règlements des élèves inscrits dans une classe pour l'année en cours"""
        try:
            annee = self._get_annee_service().get_annee_scolaire()[0]
            classe = self._get_classe(id_classe)
            return self._get_reglements_classe(classe, annee.id)
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Une erreur lors de la récupération des règlements par classe: {str(e)}")

    def get_reglements_by_classe_tranche(
        self,
        id_classe: int,
        id_tranche_pension: int,
        statut_paiement: StatutPaiementTranche | None = None,
    ) -> list[dict]:
        """Récupère, pour l'année en cours, la situation de paiement d'une tranche de pension
        de chaque élève inscrit dans une classe (totalement réglée, partiellement réglée ou rien réglé),
        éventuellement filtrée par statut de paiement"""
        try:
            annee = self._get_annee_service().get_annee_scolaire()[0]
            classe = self._get_classe(id_classe)
            tranche = self.tranche_pension_repository.findOne(id_tranche_pension, load_relations=False)
            if tranche is None:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error_code": "TRANCHE_PENSION_NOT_FOUND",
                        "message": "Tranche pension non trouvée",
                    },
                )
            if tranche.id_niveau != classe.id_niveau:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error_code": "TRANCHE_NIVEAU_DIFFERENT",
                        "message": "La tranche de pension n'appartient pas au niveau de la classe",
                    },
                )
            inscriptions = classe.inscriptions.filter(
                Inscription.id_annee == annee.id, Inscription.is_inscris == True
            ).all()

            resultats = []
            for inscription in inscriptions:
                reglements = [
                    r for r in inscription.eleve.reglements
                    if r.id_annee == annee.id and r.id_tranche_pension == id_tranche_pension
                ]
                # Seuls les règlements valides comptent dans le montant réglé
                montant_regle = round(sum(
                    r.montant for r in reglements if r.statut == StatutReglement.VALIDE
                ), 2)
                if montant_regle <= 0:
                    statut = StatutPaiementTranche.AUCUN
                elif montant_regle >= tranche.montant:
                    statut = StatutPaiementTranche.TOTAL
                else:
                    statut = StatutPaiementTranche.PARTIEL
                if statut_paiement is not None and statut != statut_paiement:
                    continue
                resultats.append({
                    "eleve": inscription.eleve,
                    "id_tranche_pension": id_tranche_pension,
                    "montant_tranche": tranche.montant,
                    "montant_regle": montant_regle,
                    "reste_a_payer": round(max(tranche.montant - montant_regle, 0), 2),
                    "statut_paiement": statut,
                    "reglements": reglements,
                })
            return resultats
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Une erreur lors de la récupération des règlements par classe et par tranche: {str(e)}")
