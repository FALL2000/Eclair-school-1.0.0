from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from common.dependencies import get_db, require_permission
from common.enumeration import Langue
from common.permissions import Action, Module
from repositories.administration.annee_repository import AnneeRepository
from repositories.administration.appreciation_repository import AppreciationRepository
from repositories.administration.bareme_repository import BaremeRepository
from repositories.administration.classe_repository import ClasseRepository
from repositories.administration.discipline_decision_repository import DisciplineDecisionRepository
from repositories.administration.groupe_matiere_evalue_repository import GroupeMatiereEvalueRepository
from repositories.administration.matiere_evalue_repository import MatiereEvalueRepository
from repositories.administration.trimestre_repository import TrimestreRepository
from repositories.evaluations.depends_evaluation_repository import DependsEvaluationRepository
from repositories.evaluations.discipline_eleve_repository import DisciplineEleveRepository
from repositories.evaluations.evaluation_repository import EvaluationRepository
from repositories.evaluations.notation_repository import NotationRepository
from repositories.inscription.inscription_repository import InscriptionRepository
from schemas.evaluations.bulletin_dto import BulletinAnnuelRequestDTO, BulletinClasseDTO
from services.evaluations.bulletin_service import BulletinService

router = APIRouter()


def get_bulletin_service(db: Session = Depends(get_db)):
    return BulletinService(
        AnneeRepository(db),
        ClasseRepository(db),
        InscriptionRepository(db),
        EvaluationRepository(db),
        DependsEvaluationRepository(db),
        TrimestreRepository(db),
        NotationRepository(db),
        MatiereEvalueRepository(db),
        GroupeMatiereEvalueRepository(db),
        BaremeRepository(db),
        AppreciationRepository(db),
        DisciplineEleveRepository(db),
        DisciplineDecisionRepository(db),
    )


@router.get(
    "/evaluation",
    summary="Générer les bulletins d'une classe pour une évaluation (année en cours)",
    status_code=200,
    response_model=BulletinClasseDTO,
)
def generer_bulletins_evaluation(
    bulletin_service: Annotated[BulletinService, Depends(get_bulletin_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.BULLETIN, Action.GENERER))],
    id_classe: Annotated[int, Query(description="Id de la classe")] = ...,
    id_evaluation: Annotated[int, Query(description="Id de l'évaluation")] = ...,
    id_eleve: Annotated[int | None, Query(description="Ne retourner que le bulletin de cet élève (optionnel)")] = None,
    langue: Annotated[Langue, Query(description="Langue du bulletin : FR (défaut) ou EN")] = Langue.FR,
):
    return bulletin_service.generer_bulletins_evaluation(id_classe, id_evaluation, id_eleve, langue)


@router.get(
    "/trimestre",
    summary="Générer les bulletins d'une classe pour un trimestre (année en cours)",
    status_code=200,
    response_model=BulletinClasseDTO,
)
def generer_bulletins_trimestre(
    bulletin_service: Annotated[BulletinService, Depends(get_bulletin_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.BULLETIN, Action.GENERER))],
    id_classe: Annotated[int, Query(description="Id de la classe")] = ...,
    id_trimestre: Annotated[int, Query(description="Id du trimestre")] = ...,
    id_eleve: Annotated[int | None, Query(description="Ne retourner que le bulletin de cet élève (optionnel)")] = None,
    langue: Annotated[Langue, Query(description="Langue du bulletin : FR (défaut) ou EN")] = Langue.FR,
):
    return bulletin_service.generer_bulletins_trimestre(id_classe, id_trimestre, id_eleve, langue)


@router.post(
    "/annuel",
    summary="Générer les bulletins annuels d'une classe (seuil de réussite et décisions de fin d'année paramétrables)",
    status_code=200,
    response_model=BulletinClasseDTO,
)
def generer_bulletins_annuels(
    data: BulletinAnnuelRequestDTO,
    bulletin_service: Annotated[BulletinService, Depends(get_bulletin_service)],
    _: Annotated[dict[str, Any], Depends(require_permission(Module.BULLETIN, Action.GENERER))],
    id_classe: Annotated[int, Query(description="Id de la classe")] = ...,
    id_eleve: Annotated[int | None, Query(description="Ne retourner que le bulletin de cet élève (optionnel)")] = None,
    langue: Annotated[Langue, Query(description="Langue du bulletin : FR (défaut) ou EN")] = Langue.FR,
):
    return bulletin_service.generer_bulletins_annuels(id_classe, data, id_eleve, langue)
