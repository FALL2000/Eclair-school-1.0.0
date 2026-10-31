import re

from fastapi import HTTPException

from models.administration.annee import Annee
from schemas.administration.annee_dto import AnneeCreateDTO, AnneeUpdateDTO, FORMAT_ANNEE
from repositories.administration.annee_repository import AnneeRepository

# Années « AAAA-AAAA » ou « AAAA/AAAA » contenues dans un libellé (ex. « Année scolaire 2026-2027 »)
ANNEES_LIBELLE = re.compile(r"(\d{4})(\s*[-/]\s*)(\d{4})")


def _decaler_annees(texte: str) -> str:
    """Remplace « 2026-2027 » par « 2027-2028 » dans un code ou un libellé"""
    return ANNEES_LIBELLE.sub(
        lambda m: f"{int(m.group(1)) + 1}{m.group(2)}{int(m.group(3)) + 1}", texte, count=1)


class AnneeService:
    def __init__(self, annee_repository: AnneeRepository):
        self.annee_repository = annee_repository

    def _check_code_exists(self, code: str):
        exist_annee = self.annee_repository.findByCode(code)
        if len(exist_annee) > 0:
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "DUPLICATION_CODE",
                    "message": f"L'année avec le code {code} existe déjà."
                }
            )

    def get_annee_scolaire(self):
        annee_scolaire = self.annee_repository.findByIs_cloture(False)
        if len(annee_scolaire) == 0:
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "NOT_FOUND_YEAR",
                    "message": "Aucune annee en cours trouve"
                }
            )
        return annee_scolaire

    def get_all_annees(self):
        """Recupere toutes les annees scolaires, de la plus recente a la plus ancienne"""
        try:
            annees = self.annee_repository.findAll(load_relations=False)
            return sorted(annees, key=lambda a: a.id, reverse=True)
        except Exception as e:
            self.annee_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la recuperation des annees: {str(e)}")

    def _annee_suivante(self, annee_recente: Annee) -> Annee:
        """Calcule l'annee qui suit la plus recente : 2026-2027 -> 2027-2028"""
        if FORMAT_ANNEE.match(annee_recente.code) is None:
            raise HTTPException(
                status_code=409,
                detail={
                    "error_code": "CALCUL_ANNEE_IMPOSSIBLE",
                    "message": f"Impossible de calculer l'année suivante : le code {annee_recente.code} n'est pas de la forme AAAA-AAAA"
                }
            )
        code = _decaler_annees(annee_recente.code)
        libelle = _decaler_annees(annee_recente.libelle) if ANNEES_LIBELLE.search(annee_recente.libelle) else code
        return Annee(code=code, libelle=libelle)

    def define_annee_scolaire(self, annee_in: AnneeCreateDTO | None):
        """Definit une annee scolaire en BD :
        - premiere annee du systeme : code et libelle fournis dans le corps de la requete ;
        - annees suivantes : l'annee en cours doit etre cloturee, la nouvelle annee est calculee
          a partir de la plus recente (2026-2027 -> 2027-2028) et le corps de la requete est ignore."""
        try:
            annees = self.annee_repository.findAll(load_relations=False)
            if len(annees) == 0:
                if annee_in is None:
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "error_code": "PREMIERE_ANNEE_REQUISE",
                            "message": "Le code et le libellé de la première année scolaire sont obligatoires"
                        }
                    )
                db_annee = Annee.model_validate(annee_in)
            else:
                en_cours = [a for a in annees if not a.is_cloture]
                if len(en_cours) > 0:
                    raise HTTPException(
                        status_code=409,
                        detail={
                            "error_code": "ANNEE_EN_COURS",
                            "message": f"Clôturez l'année en cours ({en_cours[0].libelle}) avant de passer à l'année suivante"
                        }
                    )
                db_annee = self._annee_suivante(max(annees, key=lambda a: a.id))
            self._check_code_exists(db_annee.code)
            db_annee.is_cloture = False
            new_annee = self.annee_repository.save(db_annee)
            self.annee_repository.session.commit()
            return new_annee
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.annee_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la definition  de l'annee: {str(e)}")

    def update_annee_scolaire(self, annee_update: AnneeUpdateDTO, annee_id: int):
        """Modifie une annee definie en BD ; is_cloture=True cloture l'annee en cours.
        Le code et le libelle ne sont plus modifiables des que des inscriptions sont liees a l'annee,
        et une annee cloturee ne peut pas etre rouverte."""
        try:
            db_annee = self.annee_repository.findOne(annee_id, load_relations=True)
            if db_annee is None:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error_code": "ANNEE_NOT_FOUND",
                        "message": "Annee non trouve"
                    }
                )
            update_data = annee_update.model_dump(exclude_unset=True)
            if update_data.get("is_cloture") is False and db_annee.is_cloture:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error_code": "ANNEE_CLOTUREE",
                        "message": "Une année clôturée ne peut pas être rouverte"
                    }
                )
            modifie_identite = any(
                update_data.get(cle) is not None and update_data[cle] != getattr(db_annee, cle)
                for cle in ("code", "libelle")
            )
            if modifie_identite and len(db_annee.inscriptions) > 0:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error_code": "INSCRIPTIONS_IN_ANNEE",
                        "message": "Modification impossible : des inscriptions sont déjà liées à cette année."
                    }
                )
            if annee_update.code is not None and annee_update.code != db_annee.code:
                self._check_code_exists(annee_update.code)
            for key, value in update_data.items():
                if value is not None:
                    setattr(db_annee, key, value)
            new_annee = self.annee_repository.save(db_annee)
            self.annee_repository.session.commit()
            return new_annee
        except HTTPException as http_exec:
            raise http_exec
        except Exception as e:
            self.annee_repository.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Une erreur lors de la modification  de l'annee: {str(e)}")
