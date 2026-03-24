from fastapi import FastAPI

app = FastAPI(title="Mon API Afrique")


@app.get("/")
def read_root():
    # TEST SONAR : Déclare une variable 'x = 1' ici sans l'utiliser
    return {"status": "success", "message": "Hey, Le serveur FastAPI tourne !"}
