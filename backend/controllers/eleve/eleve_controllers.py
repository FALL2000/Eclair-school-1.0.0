from fastapi import APIRouter

router = APIRouter()


@router.get("/test")
def test_eleve():
    return {"message": "Route élève de test OK"}
