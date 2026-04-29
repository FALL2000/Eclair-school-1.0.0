from datetime import date
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
    InscriptionNouveauEleveRequestDTO,
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
                inscription_id)
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
            classe = self.classe_repository.findOne(id_classe)
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
