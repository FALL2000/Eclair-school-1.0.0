from fastapi import FastAPI
from pydantic import BaseModel
import os # <--- SonarLint devrait souligner ceci (Import inutilisé)

app = FastAPI(title="Mon API Afrique")

# Modèle de données (Propre pour Sonar et FastAPI)
class Item(BaseModel):
    name: str
    price: float
    is_offer:bool = None

@app.get("/")
def read_root():
    # TEST SONAR : Déclare une variable 'x = 1' ici sans l'utiliser
    return {"status": "success", "message": "Le serveur FastAPI tourne !"}

@app.post("/items/")
def create_item(item: Item):
    return {"item_name": item.name, "item_id": 1}

@app.get("/test-security")
def security_flaw(username: str):
    # Règle de sécurité : Ne jamais utiliser eval() avec une entrée utilisateur
    return eval(username) 

