from datetime import date

from fastapi import HTTPException

from common.enumeration import FiltrePaiementTranche, StatutPaiementTranche, StatutReglement, TypeReglement
from models.inscription.inscription import Inscription
from models.scolarite.reglement import Reglement
from repositories.administration.annee_repository import AnneeRepository
from repositories.administration.classe_repository import ClasseRepository
from repositories.scolarite.reglement_repository import ReglementRepository
from repositories.scolarite.tranche_pension_repository import TranchePensionRepository
from schemas.scolarite.reglement_dto import (
    PaginatedHistoriqueReglement,
    ReglementRecuDTO,
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

    def _check_montant(self, id_eleve: int, id_tranche_pension: int, id_annee: int, montant: float, type_reglement,
                       exclude_id: int | None = None):
        """Contrôles d'un règlement : élève inscrit cette année, tranche de son niveau, tranche pas encore soldée,
        montant au plus égal au reste ; total = solde exactement le reste, partiel = montant inférieur au reste"""
        id_niveau = self.reglement_repository.niveau_eleve_annee(id_eleve, id_annee)
        if id_niveau is None:
            raise HTTPException(
                status_code=400,
                detail={"error_code": "ELEVE_NON_INSCRIT", "message": "L'élève n'est pas inscrit pour l'année en cours"},
            )
        tranche = self.tranche_pension_repository.findOne(id_tranche_pension, load_relations=False)
        if tranche is None:
            raise HTTPException(
                status_code=404,
                detail={"error_code": "TRANCHE_PENSION_NOT_FOUND", "message": "Tranche de pension non trouvée"},
            )
        if tranche.id_niveau != id_niveau:
            raise HTTPException(
                status_code=400,
                detail={"error_code": "TRANCHE_NIVEAU_DIFFERENT", "message": "Cette tranche n'appartient pas au niveau de l'élève"},
            )
        reste = round(tranche.montant - self.reglement_repository.total_regle(id_eleve, id_tranche_pension, id_annee, exclude_id), 2)
        if reste <= 0:
            raise HTTPException(
                status_code=409,
                detail={"error_code": "TRANCHE_DEJA_REGLEE", "message": "Cette tranche est déjà entièrement réglée"},
            )
        if montant > reste:
            raise HTTPException(
                status_code=400,
                detail={"error_code": "MONTANT_SUPERIEUR_AU_RESTE", "message": f"Le montant dépasse le reste à payer ({reste:g} FCFA)"},
            )
        type_attendu = TypeReglement.TOTAL if montant == reste else TypeReglement.PARTIEL
        if type_reglement is not None and TypeReglement(type_reglement) != type_attendu:
            raise HTTPException(
                status_code=400,
                detail={"error_code": "TYPE_REGLEMENT_INCOHERENT",
                        "message": f"Un règlement total doit solder le reste ({reste:g} FCFA) ; un règlement partiel doit être inférieur au reste"},
            )
        return type_attendu

    def add_reglement(self, reglement_in: ReglementCreateDTO, id_eleve: int, id_tranche_pension: int, current_user: dict):
        """Enregistre un règlement total ou partiel pour l'année scolaire en cours"""
        try:
            annee = self._get_annee_service().get_annee_scolaire()[0]
            self._check_montant(id_eleve, id_tranche_pension, annee.id, reglement_in.montant, reglement_in.type)
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
            if ("montant" in update_data or "type" in update_data) and db_reglement.statut == StatutReglement.VALIDE:
                # Mêmes contrôles qu'à l'ajout, sans compter le règlement modifié dans le total déjà réglé
                self._check_montant(
                    db_reglement.id_eleve, db_reglement.id_tranche_pension, db_reglement.id_annee,
                    update_data.get("montant", db_reglement.montant), update_data.get("type", db_reglement.type),
                    exclude_id=db_reglement.id)
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
        statut_paiement: FiltrePaiementTranche | None = None,
    ) -> list[dict]:
        """Récupère, pour l'année en cours, la situation de paiement d'une tranche de pension
        de chaque élève inscrit dans une classe (totalement réglée, partiellement réglée ou rien réglé),
        triée par nom puis prénom, éventuellement filtrée par statut de paiement
        (non_solde = partiel et aucun ensemble). Sert aussi à l'export PDF généré dans Angular."""
        if statut_paiement is None:
            statuts_retenus = None
        elif statut_paiement == FiltrePaiementTranche.NON_SOLDE:
            statuts_retenus = {StatutPaiementTranche.PARTIEL, StatutPaiementTranche.AUCUN}
        else:
            statuts_retenus = {StatutPaiementTranche(statut_paiement.value)}
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
                if statuts_retenus is not None and statut not in statuts_retenus:
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
            resultats.sort(key=lambda x: ((x["eleve"].nom or "").lower(), (x["eleve"].prenom or "").lower()))
            return resultats
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Une erreur lors de la récupération des règlements par classe et par tranche: {str(e)}")

    def get_historique(
        self, date_debut: date | None, date_fin: date | None, q: str | None,
        page: int | None, page_size: int | None, statut: StatutReglement | None = None,
    ) -> PaginatedHistoriqueReglement:
        """Historique des règlements de l'année scolaire en cours, du plus récent au plus ancien, paginé.
        Filtres optionnels : intervalle de dates de règlement, nom, prénom ou matricule de l'élève, statut (valide, annule)."""
        try:
            if date_debut and date_fin and date_debut > date_fin:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error_code": "INTERVALLE_DATES_INVALIDE",
                        "message": "La date de debut doit etre anterieure ou egale a la date de fin",
                    },
                )
            annee = self._get_annee_service().get_annee_scolaire()[0]
            termes = [terme for terme in (q or "").split() if terme]
            total_items, total_valide = self.reglement_repository.count_historique(annee.id, date_debut, date_fin, termes, statut)
            if page_size is None or page is None:
                page_size = total_items if total_items > 0 else 1
                page = 1
            total_pages = max(1, (total_items + page_size - 1) // page_size)
            page = min(max(page, 1), total_pages)
            lignes = self.reglement_repository.find_historique(
                annee.id, date_debut, date_fin, termes, offset=(page - 1) * page_size, limit=page_size, statut=statut)
            return PaginatedHistoriqueReglement(
                total_valide=round(total_valide, 2),
                page=page,
                page_size=page_size,
                total_items=total_items,
                total_pages=total_pages,
                reglements=[{
                    "id": r.id, "date_reglement": r.date_reglement, "type": r.type, "montant": r.montant,
                    "statut": r.statut, "id_annee": r.id_annee, "id_tranche_pension": r.id_tranche_pension,
                    "tranche": tranche, "id_eleve": eleve.id, "matricule": eleve.matricule, "nom": eleve.nom,
                    "prenom": eleve.prenom, "id_classe": id_classe, "classe": classe,
                    "id_user": r.id_user, "user": user,
                } for r, eleve, tranche, id_classe, classe, user in lignes],
            )
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la recuperation de l'historique des reglements: {str(e)}")

    @staticmethod
    def numero_recu(reglement: Reglement) -> str:
        """Numéro du reçu de règlement : REG-<année du règlement>-<id sur 6 chiffres>"""
        return f"REG-{reglement.date_reglement.year}-{reglement.id:06d}"

    def get_recu(self, reglement_id: int) -> ReglementRecuDTO:
        """Données du reçu d'un règlement (ou de son duplicata) : élève, classe de l'année, tranche,
        montant versé, cumul versé pour la tranche jusqu'à ce règlement et reste à payer"""
        try:
            ligne = self.reglement_repository.find_ligne_recu(reglement_id)
            if ligne is None:
                self._check_reglement_exists(None)
            r, eleve, tranche_libelle, id_classe, classe, user = ligne
            tranche = self.tranche_pension_repository.findOne(r.id_tranche_pension, load_relations=False)
            annee = self.annee_repository.findOne(r.id_annee)
            cumul = round(self.reglement_repository.cumul_tranche(r), 2)
            return ReglementRecuDTO(
                id=r.id, date_reglement=r.date_reglement, type=r.type, montant=r.montant, statut=r.statut,
                id_annee=r.id_annee, id_tranche_pension=r.id_tranche_pension, tranche=tranche_libelle,
                id_eleve=eleve.id, matricule=eleve.matricule, nom=eleve.nom, prenom=eleve.prenom,
                id_classe=id_classe, classe=classe, id_user=r.id_user, user=user,
                numero=self.numero_recu(r),
                annee=annee.libelle if annee else "",
                numero_ordre_tranche=tranche.numero_ordre,
                montant_tranche=tranche.montant,
                cumul_verse=cumul,
                reste_a_payer=round(max(tranche.montant - cumul, 0), 2),
            )
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la recuperation du recu: {str(e)}")
