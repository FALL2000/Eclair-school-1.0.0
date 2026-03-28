from utils.logger import get_logger
from fastapi import FastAPI

app = FastAPI(title="Mon API Afrique")
logger = get_logger()


@app.get("/")
def read_root():
    # TEST SONAR : Déclare une variable 'x = 1' ici sans l'utiliser
    logger.info('APP DEMARRE')
    return {"status": "success", "message": "Hey, Le serveur FastAPI tourne !"}
