FROM python:3.12-slim

# 1. Création de l'utilisateur et dépendances système
RUN useradd -m myuser
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 2. Installation des dépendances Python (en root pour le cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copie du code
COPY . .

# 4. GESTION DES PERMISSIONS
# On crée le dossier logs s'il n'existe pas
RUN mkdir -p /app/logs && \
    # On donne la propriété de tout le dossier à myuser
    chown -R myuser:myuser /app && \
    # On donne les droits d'exécution au script
    chmod +x start.sh && \
    # OPTIONNEL : On peut laisser le reste en 555, 
    # Le dossier logs DOIT être en 755 (écriture autorisée pour le propriétaire)
    chmod -R 555 /app && \
    chmod -R 755 /app/logs

# 5. Passage à l'utilisateur non-privilégié
USER myuser

EXPOSE 8000

# 6. Lancement du script
# Note : uvicorn est déjà appelé à l'intérieur de ton start.sh, 
# donc on n'a pas besoin de le remettre ici sauf si ton script utilise des arguments $@
CMD ["./start.sh"]