import calendar
import re
from datetime import date, datetime

from fastapi import HTTPException

from common.enumeration import MOYENS_PAIEMENT_AVEC_COMPTE, StatutPaiementTranche, StatutReglement
from common.permissions import Action, Module, code_permission
from models.enseignants.enseignant import Enseignant
from models.enseignants.versement_salaire import VersementSalaire
from repositories.administration.annee_repository import AnneeRepository
from repositories.administration.configuration_repository import ConfigurationRepository
from repositories.enseignants.enseignant_repository import EnseignantRepository
from repositories.enseignants.versement_salaire_repository import VersementSalaireRepository
from schemas.enseignants.salaire_dto import (
    MoyenPaiementUpdateDTO,
    PaginatedMoyenPaiement,
    PaginatedSalaireMois,
    PaginatedVersementSalaire,
    VersementSalaireCreateDTO,
)
from services.administration.annee_service import AnneeService


# Le numero de compte complet n'est visible que par ceux qui gerent les salaires
PERMISSIONS_NUMERO_COMPTE = (
    code_permission(Module.SALAIRE, Action.AJOUTER),
    code_permission(Module.SALAIRE, Action.MODIFIER),
)


def peut_voir_numero_compte(current_user: dict) -> bool:
    return current_user.get("is_super_admin", False) or any(
        code in current_user.get("permissions", []) for code in PERMISSIONS_NUMERO_COMPTE)


def masquer_numero_compte(numero: str | None) -> str | None:
    """Ne garde que les 4 derniers caracteres : « 10005 00001 01234567890 12 » -> « •••• 9012 »"""
    if not numero:
        return numero
    compact = numero.replace(" ", "")
    return f"•••• {compact[-4:]}" if len(compact) > 4 else "••••"


def _duree_heures(heure_deb, heure_fin) -> float:
    return (datetime.combine(date.min, heure_fin) - datetime.combine(date.min, heure_deb)).total_seconds() / 3600


class SalaireService:
    """Salaires des enseignants : montant du par mois (fixe pour un salaire mensuel, heures payees x taux
    pour un salaire horaire), versements totaux ou partiels et reste a verser"""

    def __init__(
        self,
        versement_repository: VersementSalaireRepository,
        enseignant_repository: EnseignantRepository,
        annee_repository: AnneeRepository,
        configuration_repository: ConfigurationRepository,
    ):
        self.versement_repository = versement_repository
        self.enseignant_repository = enseignant_repository
        self.annee_repository = annee_repository
        self.configuration_repository = configuration_repository

    def _session(self):
        return self.versement_repository.session

    def _get_annee(self, annee_civile: int):
        """Annee scolaire en cours ; l'annee civile doit etre l'une de celles qui la composent (ex : 2026 ou 2027)"""
        annee = AnneeService(self.annee_repository).get_annee_scolaire()[0]
        annees_civiles = {int(a) for a in re.findall(r"\d{4}", annee.libelle or "")}
        if annees_civiles and annee_civile not in annees_civiles:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code": "MOIS_HORS_ANNEE_SCOLAIRE",
                    "message": f"Le mois doit appartenir a l'annee scolaire {annee.libelle}",
                },
            )
        return annee

    def _absences_justifiees_payees(self) -> bool:
        configurations = self.configuration_repository.findAll()
        return bool(configurations and configurations[0].is_absence_justifiee_payee)

    @staticmethod
    def _est_horaire(enseignant: Enseignant) -> bool:
        type_salaire = enseignant.type_salaire
        return type_salaire is not None and "hor" in f"{type_salaire.code} {type_salaire.libelle}".lower()

    def _calculer(self, enseignants: list[Enseignant], mois: int, annee_civile: int, id_annee: int) -> dict[int, dict]:
        """Montant du du mois et heures payees par enseignant"""
        debut = date(annee_civile, mois, 1)
        fin = date(annee_civile, mois, calendar.monthrange(annee_civile, mois)[1])
        horaires = [e.id for e in enseignants if self._est_horaire(e)]
        heures: dict[int, float] = {}
        for id_enseignant, heure_deb, heure_fin in self.versement_repository.seances_payees(
                debut, fin, id_annee, self._absences_justifiees_payees(), horaires):
            heures[id_enseignant] = heures.get(id_enseignant, 0) + _duree_heures(heure_deb, heure_fin)
        resultat = {}
        for e in enseignants:
            taux = e.montant_salaire or 0
            if self._est_horaire(e):
                nb_heures = round(heures.get(e.id, 0), 2)
                resultat[e.id] = {"nb_heures": nb_heures, "montant_du": round(nb_heures * taux, 2)}
            else:
                resultat[e.id] = {"nb_heures": None, "montant_du": round(taux, 2)}
        return resultat

    def _situation(self, e: Enseignant, calcul: dict, verse: float) -> dict:
        montant_du = calcul["montant_du"]
        verse = round(verse, 2)
        if verse <= 0:
            statut = StatutPaiementTranche.AUCUN
        elif verse >= montant_du:
            statut = StatutPaiementTranche.TOTAL
        else:
            statut = StatutPaiementTranche.PARTIEL
        return {
            "id_enseignant": e.id,
            "nom": e.nom,
            "prenom": e.prenom,
            "is_active": e.is_active,
            "type_salaire": e.type_salaire.libelle if e.type_salaire else "",
            "is_horaire": self._est_horaire(e),
            "taux": e.montant_salaire,
            "nb_heures": calcul["nb_heures"],
            "montant_du": montant_du,
            "montant_verse": verse,
            "reste": round(max(montant_du - verse, 0), 2),
            "statut_paiement": statut,
            "moyen_paiement": e.moyen_paiement,
        }

    def get_salaires_mois(
        self, mois: int, annee_civile: int, q: str | None, statut: StatutPaiementTranche | None,
        page: int | None, page_size: int | None, id_matiere: int | None = None,
    ) -> PaginatedSalaireMois:
        """Salaires d'un mois pour tous les enseignants (actifs et inactifs) : du, verse, reste et statut, pagines et tries par nom.
        Filtres : nom ou prenom, matiere enseignee, statut de paiement"""
        try:
            annee = self._get_annee(annee_civile)
            termes = [terme for terme in (q or "").split() if terme]
            enseignants = self.enseignant_repository.find_pour_salaire(termes, id_matiere)
            calculs = self._calculer(enseignants, mois, annee_civile, annee.id)
            verses = self.versement_repository.totaux_verses(mois, annee_civile)
            lignes = [self._situation(e, calculs[e.id], verses.get(e.id, 0)) for e in enseignants]
            if statut is not None:
                lignes = [l for l in lignes if l["statut_paiement"] == statut]
            total_items = len(lignes)
            if page_size is None or page is None:
                page_size = total_items if total_items > 0 else 1
                page = 1
            total_pages = max(1, (total_items + page_size - 1) // page_size)
            page = min(max(page, 1), total_pages)
            return PaginatedSalaireMois(
                mois=mois,
                annee_civile=annee_civile,
                total_du=round(sum(l["montant_du"] for l in lignes), 2),
                total_verse=round(sum(min(l["montant_verse"], l["montant_du"]) for l in lignes), 2),
                total_reste=round(sum(l["reste"] for l in lignes), 2),
                page=page,
                page_size=page_size,
                total_items=total_items,
                total_pages=total_pages,
                salaires=lignes[(page - 1) * page_size: page * page_size],
            )
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la recuperation des salaires: {str(e)}")

    def _get_enseignant(self, id_enseignant: int) -> Enseignant:
        enseignant = self.enseignant_repository.findOne(id_enseignant, load_relations=True)
        if enseignant is None:
            raise HTTPException(
                status_code=404,
                detail={"error_code": "ENSEIGNANT_NOT_FOUND", "message": "Enseignant non trouve"},
            )
        return enseignant

    def get_salaire_enseignant(self, id_enseignant: int, mois: int, annee_civile: int, voir_numero_compte: bool = False):
        """Situation du salaire d'un enseignant pour un mois, avec ses versements et son compte de paiement"""
        try:
            annee = self._get_annee(annee_civile)
            enseignant = self._get_enseignant(id_enseignant)
            calcul = self._calculer([enseignant], mois, annee_civile, annee.id)[enseignant.id]
            verse = self.versement_repository.totaux_verses(mois, annee_civile).get(enseignant.id, 0)
            return {
                **self._situation(enseignant, calcul, verse),
                "mois": mois,
                "annee_civile": annee_civile,
                "numero_compte": enseignant.numero_compte if voir_numero_compte else masquer_numero_compte(enseignant.numero_compte),
                "intitule_compte": enseignant.intitule_compte,
                "versements": self.versement_repository.versements(enseignant.id, mois, annee_civile),
            }
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la recuperation du salaire: {str(e)}")

    def verser_salaire(self, data: VersementSalaireCreateDTO, current_user: dict):
        """Enregistre un versement (total ou partiel) ; il ne peut pas depasser le reste a verser du mois.
        Aucun versement pour un enseignant inactif"""
        try:
            if data.date_versement > date.today():
                raise HTTPException(
                    status_code=400,
                    detail={"error_code": "DATE_VERSEMENT_FUTURE", "message": "La date du versement ne peut pas etre dans le futur"},
                )
            annee = self._get_annee(data.annee_civile)
            enseignant = self._get_enseignant(data.id_enseignant)
            if not enseignant.is_active:
                raise HTTPException(
                    status_code=409,
                    detail={"error_code": "ENSEIGNANT_INACTIF", "message": "Impossible d'enregistrer un versement pour un enseignant inactif"},
                )
            calcul = self._calculer([enseignant], data.mois, data.annee_civile, annee.id)[enseignant.id]
            if calcul["montant_du"] <= 0:
                raise HTTPException(
                    status_code=400,
                    detail={"error_code": "AUCUN_MONTANT_DU", "message": "Aucun salaire n'est du pour ce mois"},
                )
            verse = self.versement_repository.totaux_verses(data.mois, data.annee_civile).get(enseignant.id, 0)
            reste = round(calcul["montant_du"] - verse, 2)
            if round(data.montant, 2) > reste:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error_code": "MONTANT_SUPERIEUR_AU_RESTE",
                        "message": f"Le montant depasse le reste a verser pour ce mois ({reste})",
                    },
                )
            versement = VersementSalaire(
                id_enseignant=enseignant.id,
                id_annee=annee.id,
                mois=data.mois,
                annee_civile=data.annee_civile,
                montant=round(data.montant, 2),
                montant_du=calcul["montant_du"],
                nb_heures=calcul["nb_heures"],
                date_versement=data.date_versement,
                statut=StatutReglement.VALIDE,
                id_user=current_user["id"],
            )
            nouveau = self.versement_repository.save(versement)
            self._session().commit()
            return nouveau
        except HTTPException as http_exec:
            self._session().rollback()
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'enregistrement du versement: {str(e)}")

    def annuler_versement(self, versement_id: int):
        """Annule un versement (il n'est plus compte dans le montant verse)"""
        try:
            versement = self.versement_repository.findOne(versement_id)
            if versement is None:
                raise HTTPException(
                    status_code=404,
                    detail={"error_code": "VERSEMENT_NOT_FOUND", "message": "Versement non trouve"},
                )
            if versement.statut == StatutReglement.ANNULE:
                raise HTTPException(
                    status_code=409,
                    detail={"error_code": "VERSEMENT_DEJA_ANNULE", "message": "Le versement est deja annule"},
                )
            versement.statut = StatutReglement.ANNULE
            mis_a_jour = self.versement_repository.save(versement)
            self._session().commit()
            return mis_a_jour
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de l'annulation du versement: {str(e)}")

    def get_versements(
        self, mois: int | None, annee_civile: int | None, q: str | None, id_matiere: int | None,
        page: int | None, page_size: int | None,
    ) -> PaginatedVersementSalaire:
        """Versements de l'annee scolaire en cours (plusieurs versements possibles pour un meme mois),
        du plus recent au plus ancien, pagines. Filtres : mois, nom ou prenom, matiere enseignee"""
        try:
            if (mois is None) != (annee_civile is None):
                raise HTTPException(
                    status_code=400,
                    detail={"error_code": "MOIS_INCOMPLET", "message": "Le mois et l'annee civile doivent etre renseignes ensemble"},
                )
            if annee_civile is not None:
                annee = self._get_annee(annee_civile)
            else:
                annee = AnneeService(self.annee_repository).get_annee_scolaire()[0]
            termes = [terme for terme in (q or "").split() if terme]
            total_items, total_verse = self.versement_repository.count_versements(annee.id, mois, annee_civile, termes, id_matiere)
            if page_size is None or page is None:
                page_size = total_items if total_items > 0 else 1
                page = 1
            total_pages = max(1, (total_items + page_size - 1) // page_size)
            page = min(max(page, 1), total_pages)
            lignes = self.versement_repository.find_versements(
                annee.id, mois, annee_civile, termes, id_matiere, offset=(page - 1) * page_size, limit=page_size)
            return PaginatedVersementSalaire(
                total_verse=round(total_verse, 2),
                page=page,
                page_size=page_size,
                total_items=total_items,
                total_pages=total_pages,
                versements=[{**versement.model_dump(), "nom": nom, "prenom": prenom, "user": user}
                            for versement, nom, prenom, user in lignes],
            )
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la recuperation des versements: {str(e)}")

    def get_moyens_paiement(
        self, configure: bool | None, q: str | None, id_matiere: int | None,
        page: int | None, page_size: int | None, voir_numero_compte: bool,
    ) -> PaginatedMoyenPaiement:
        """Moyens de paiement des enseignants actifs, pagines et tries par nom.
        configure=False : enseignants dont le moyen de paiement n'est pas encore renseigne"""
        try:
            termes = [terme for terme in (q or "").split() if terme]
            total_items = self.enseignant_repository.count_moyens_paiement(termes, id_matiere, configure)
            if page_size is None or page is None:
                page_size = total_items if total_items > 0 else 1
                page = 1
            total_pages = max(1, (total_items + page_size - 1) // page_size)
            page = min(max(page, 1), total_pages)
            enseignants = self.enseignant_repository.find_moyens_paiement(
                termes, id_matiere, configure, offset=(page - 1) * page_size, limit=page_size)
            return PaginatedMoyenPaiement(
                nb_non_configures=self.enseignant_repository.count_moyens_paiement([], None, False),
                page=page,
                page_size=page_size,
                total_items=total_items,
                total_pages=total_pages,
                enseignants=[{
                    "id_enseignant": e.id,
                    "nom": e.nom,
                    "prenom": e.prenom,
                    "telephone1": e.telephone1,
                    "type_salaire": e.type_salaire.libelle if e.type_salaire else "",
                    "moyen_paiement": e.moyen_paiement,
                    "numero_compte": e.numero_compte if voir_numero_compte else masquer_numero_compte(e.numero_compte),
                    "intitule_compte": e.intitule_compte,
                } for e in enseignants],
            )
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la recuperation des moyens de paiement: {str(e)}")

    def configurer_moyen_paiement(self, id_enseignant: int, data: MoyenPaiementUpdateDTO):
        """Renseigne ou modifie le moyen de paiement d'un enseignant.
        COMPTE BANCAIRE ou MOBILE : numero de compte obligatoire ; ESPECE : numero et intitule effaces"""
        try:
            enseignant = self._get_enseignant(id_enseignant)
            numero = (data.numero_compte or "").strip() or None
            intitule = (data.intitule_compte or "").strip() or None
            if data.moyen_paiement in MOYENS_PAIEMENT_AVEC_COMPTE:
                if numero is None:
                    raise HTTPException(
                        status_code=400,
                        detail={"error_code": "NUMERO_COMPTE_OBLIGATOIRE",
                                "message": "Le numero de compte est obligatoire pour un paiement par compte bancaire ou mobile"},
                    )
            else:
                numero = intitule = None
            enseignant.moyen_paiement = data.moyen_paiement
            enseignant.numero_compte = numero
            enseignant.intitule_compte = intitule
            self.enseignant_repository.save(enseignant)
            self.versement_repository.session.commit()
            return {
                "id_enseignant": enseignant.id,
                "nom": enseignant.nom,
                "prenom": enseignant.prenom,
                "telephone1": enseignant.telephone1,
                "type_salaire": enseignant.type_salaire.libelle if enseignant.type_salaire else "",
                "moyen_paiement": enseignant.moyen_paiement,
                "numero_compte": enseignant.numero_compte,
                "intitule_compte": enseignant.intitule_compte,
            }
        except HTTPException as http_exec:
            self.versement_repository.session.rollback()
            raise http_exec
        except Exception as e:
            self.versement_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la configuration du moyen de paiement: {str(e)}")
