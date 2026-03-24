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

# 4. GESTION DES PERMISSIONS (TOUJOURS EN ROOT)
# On donne les droits d'exécution à start.sh AVANT de restreindre le reste
RUN chmod +x start.sh && \
    # Puis on passe tout en lecture seule (555 = Lecture + Exécution partout)
    chmod -R 555 /app

# 5. Passage à l'utilisateur non-privilégié
USER myuser

EXPOSE 8000

# 6. Lancement du script
# Note : uvicorn est déjà appelé à l'intérieur de ton start.sh, 
# donc on n'a pas besoin de le remettre ici sauf si ton script utilise des arguments $@
CMD ["./start.sh"]