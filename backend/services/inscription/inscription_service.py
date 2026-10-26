from datetime import date, datetime
import random
import string
from typing import List

from fastapi import HTTPException

from models.administration.classe import Classe
from repositories.administration.classe_repository import ClasseRepository
from models.administration.annee import Annee
from services.administration.annee_service import AnneeService
from repositories.administration.annee_repository import AnneeRepository
from models.eleve.eleve import Eleve
from models.inscription.inscription import Inscription
from repositories.eleve.eleve_repository import EleveRepository
from repositories.inscription.inscription_repository import InscriptionRepository
from schemas.inscription.inscription_dto import (
    InscriptionModificationDTO,
    InscriptionNouveauEleveRequestDTO,
    PaginatedHistoriqueInscription,
    PaginatedInscription,
)


class InscriptionService:
    def __init__(
        self,
        eleve_repository: EleveRepository,
        inscription_repository: InscriptionRepository,
        classe_repository: ClasseRepository,
    ):
        self.eleve_repository = eleve_repository
        self.inscription_repository = inscription_repository
        self.classe_repository = classe_repository

    def _session(self):
        return self.inscription_repository.session

    def _get_annee_service(self):
        annee_repo = AnneeRepository(self._session())
        return AnneeService(annee_repo)

    def _generer_matricule(self, annee_scolaire: List[Annee]):
        """Genere le matricule d'un nouveau eleve inscris. ex: 25F0021
           25-> prefixe annee(2025-2026), F-> lettre aleatoire
           0021 -> rang de l'eleve inscris formate, dans l'exemple c'est 21e nouveau eleve inscris dans l'annee
        """
        new_eleve_inscris = self.inscription_repository.findBy(
            is_nouveau=True, id_annee=annee_scolaire[0].id)
        first_part_annee = annee_scolaire[0].libelle.split("-")[0]
        prefixe_annee = first_part_annee[-2:]
        lettre_aleatoire = random.choice(string.ascii_uppercase)
        number_formate = f"{(len(new_eleve_inscris) + 1):04d}"
        matricule = f"{prefixe_annee}{lettre_aleatoire}{number_formate}"
        return matricule

    def _check_matricule_exists(self, matricule: str):
        exist = self.eleve_repository.findByMatricule(matricule)
        if len(exist) > 0:
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "DUPLICATION_MATRICULE",
                    "message": f"L'eleve avec le matricule {matricule} existe deja.",
                },
            )

    def _check_inscription_exists(self, db_inscription: Inscription | None):
        if db_inscription is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "INSCRIPTION_NOT_FOUND",
                    "message": "Inscription non trouvee",
                },
            )

    def inscrire_nouveau_eleve(self, data: InscriptionNouveauEleveRequestDTO, current_user: dict):
        """Cree l'eleve puis l'inscription (inscription finalisee : is_inscris True, date du jour)."""
        try:
            annee_scolaire = self._get_annee_service().get_annee_scolaire()
            eleve_dict = data.eleve.model_dump()
            eleve_dict["matricule"] = self._generer_matricule(annee_scolaire)
            db_eleve = Eleve.model_validate(eleve_dict)
            new_eleve = self.eleve_repository.save(db_eleve)

            db_inscription = Inscription(
                id_eleve=new_eleve.id,
                id_classe=data.id_classe,
                id_annee=annee_scolaire[0].id,
                is_redoublant=data.is_redoublant,
                is_nouveau=data.is_nouveau,
                id_user=current_user["id"],
                date_inscris=date.today(),
                is_inscris=True,
            )
            new_inscription = self.inscription_repository.save(db_inscription)
            self._session().commit()
            return new_inscription
        except HTTPException as http_exec:
            self._session().rollback()
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Une erreur lors de l'inscription du nouvel eleve: {str(e)}",
            )

    def finaliser_inscription_ancien_eleve(self, inscription_id: int, current_user: dict):
        """Met a jour une inscription existante (is_inscris False) : is_inscris True et date_inscris."""
        try:
            db_inscription = self.inscription_repository.findOne(
                inscription_id, load_relations=True)
            self._check_inscription_exists(db_inscription)
            if db_inscription.is_inscris:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error_code": "INSCRIPTION_DEJA_FINALISEE",
                        "message": "L'inscription est deja finalisee (is_inscris est True).",
                    },
                )
            db_inscription.is_inscris = True
            db_inscription.date_inscris = date.today()
            db_inscription.id_user = current_user["id"]
            updated = self.inscription_repository.save(db_inscription)
            self._session().commit()
            return updated
        except HTTPException as http_exec:
            self._session().rollback()
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Une erreur lors de la finalisation de l'inscription: {str(e)}",
            )

    def get_inscriptions_by_classe(self, id_classe: int, page: int | None, page_size: int | None):
        """Recupere les eleves inscris d'une classe pour l'annee scolaire en cours,
           la liste retourne est pagines en fonction de page et page_size
        """
        try:
            annee_scolaire = self._get_annee_service().get_annee_scolaire()
            classe = self.classe_repository.findOne(id_classe, load_relations=True)
            if classe is None:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error_code": "CLASSE_NOT_FOUND",
                        "message": "Classe non trouvee"
                    }
                )
            return self._paginated_inscription_response(classe, annee_scolaire, page, page_size)
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Une erreur lors de la recuperation des inscriptions de la classe: {str(e)}",
            )

    def _paginated_inscription_response(self, classe: Classe, annee_scolaire: List[Annee], page: int | None, page_size: int | None):
        """Traite et retourne la reponse pagine de la liste des eleves 
        dans une annee scolaire en cours et une classe donnee

        Args:
            classe (Classe): classe dont on veut paginer les eleves inscris
            annee_scolaire (List[Annee]): Annee scolaire en cours
            page (int): Numero de la page pour la pagination 
            page_size (int): Nombre d'elements par page pour la pagination

        Returns:
            PaginatedInscription: liste des eleves inscris pagines
        """
        filter_list = classe.inscriptions
        base_q = filter_list.filter(
            Inscription.id_annee == annee_scolaire[0].id)

        total_items = base_q.count()
        if page_size == None or page == None:
            page_size = total_items if total_items > 0 else 1
            page = 1
        total_pages = (total_items + page_size - 1) // page_size
        if page > total_pages:
            page = total_pages

        items = base_q.offset(
            (page - 1) * page_size).limit(page_size).all() if page > 0 else []

        return PaginatedInscription(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
            inscriptions=items,
        )

    @staticmethod
    def _ligne_historique(ligne) -> dict:
        inscription, eleve, classe, niveau, user, user_modification = ligne
        return {
            "id": inscription.id,
            "date_inscris": inscription.date_inscris,
            "is_redoublant": inscription.is_redoublant,
            "is_nouveau": inscription.is_nouveau,
            "id_eleve": eleve.id,
            "matricule": eleve.matricule,
            "nom": eleve.nom,
            "prenom": eleve.prenom,
            "genre": eleve.genre,
            "dat_naissance": eleve.dat_naissance,
            "lieu_naissance": eleve.lieu_naissance,
            "id_classe": classe.id,
            "classe": classe.libelle,
            "id_niveau": niveau.id,
            "niveau": niveau.libelle,
            "id_user": inscription.id_user,
            "user": user,
            "date_modification": inscription.date_modification,
            "id_user_modification": inscription.id_user_modification,
            "user_modification": user_modification,
        }

    def get_historique(
        self, date_debut: date | None, date_fin: date | None, q: str | None,
        page: int | None, page_size: int | None,
    ) -> PaginatedHistoriqueInscription:
        """Historique des inscriptions finalisees, de la plus recente a la plus ancienne, pagine.
        Filtres optionnels : intervalle de dates d'inscription et nom, prenom ou matricule."""
        try:
            if date_debut and date_fin and date_debut > date_fin:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error_code": "INTERVALLE_DATES_INVALIDE",
                        "message": "La date de debut doit etre anterieure ou egale a la date de fin",
                    },
                )
            termes = [terme for terme in (q or "").split() if terme]
            total_items = self.inscription_repository.count_historique(date_debut, date_fin, termes)
            if page_size is None or page is None:
                page_size = total_items if total_items > 0 else 1
                page = 1
            total_pages = max(1, (total_items + page_size - 1) // page_size)
            page = min(max(page, 1), total_pages)
            lignes = self.inscription_repository.find_historique(
                date_debut, date_fin, termes, offset=(page - 1) * page_size, limit=page_size)
            return PaginatedHistoriqueInscription(
                page=page,
                page_size=page_size,
                total_items=total_items,
                total_pages=total_pages,
                inscriptions=[self._ligne_historique(ligne) for ligne in lignes],
            )
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la recuperation de l'historique des inscriptions: {str(e)}")

    def update_inscription(self, inscription_id: int, data: InscriptionModificationDTO, current_user: dict):
        """Modifie la classe (et donc le niveau) ou le statut redoublant d'une inscription de l'annee en cours.
        Le changement de classe est refuse si l'eleve a deja des notes, une discipline ou des presences
        dans l'annee en cours, ou des reglements si le niveau change (les tranches dependent du niveau)."""
        try:
            db_inscription = self.inscription_repository.findOne(inscription_id)
            self._check_inscription_exists(db_inscription)
            annee = self._get_annee_service().get_annee_scolaire()[0]
            if db_inscription.id_annee != annee.id:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error_code": "INSCRIPTION_ANNEE_CLOTUREE",
                        "message": "Seules les inscriptions de l'annee scolaire en cours sont modifiables",
                    },
                )
            modifiee = False
            if data.id_classe is not None and data.id_classe != db_inscription.id_classe:
                nouvelle_classe = self.classe_repository.findOne(data.id_classe)
                if nouvelle_classe is None:
                    raise HTTPException(
                        status_code=404,
                        detail={"error_code": "CLASSE_NOT_FOUND", "message": "Classe non trouvee"},
                    )
                donnees = self.inscription_repository.donnees_eleve_annee(db_inscription.id_eleve, annee.id)
                ancienne_classe = self.classe_repository.findOne(db_inscription.id_classe)
                if ancienne_classe.id_niveau != nouvelle_classe.id_niveau and \
                        self.inscription_repository.has_reglements_annee(db_inscription.id_eleve, annee.id):
                    donnees.append("reglements")
                if donnees:
                    raise HTTPException(
                        status_code=409,
                        detail={
                            "error_code": "MODIFICATION_CLASSE_IMPOSSIBLE",
                            "message": "Impossible de changer la classe : l'eleve a deja des donnees dans l'annee en cours",
                            "donnees": donnees,
                        },
                    )
                db_inscription.id_classe = data.id_classe
                modifiee = True
            if data.is_redoublant is not None and data.is_redoublant != db_inscription.is_redoublant:
                db_inscription.is_redoublant = data.is_redoublant
                modifiee = True
            if modifiee:
                db_inscription.date_modification = datetime.now()
                db_inscription.id_user_modification = current_user["id"]
                self.inscription_repository.save(db_inscription)
                self._session().commit()
            return self._ligne_historique(self.inscription_repository.find_ligne_historique(inscription_id))
        except HTTPException as http_exec:
            self._session().rollback()
            raise http_exec
        except Exception as e:
            self._session().rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification de l'inscription: {str(e)}")
