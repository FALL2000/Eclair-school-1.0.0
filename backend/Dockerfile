FROM python:3.12-slim

# 1. Création de l'utilisateur
RUN useradd -m myuser
WORKDIR /app

# 2. Installation des dépendances (en tant que root pour le cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copie du code (Propriété à root, lecture seule pour les autres)
# On NE met PAS de --chown ici, donc les fichiers appartiennent à root par défaut
COPY . .

# 4. On s'assure que l'utilisateur peut seulement LIRE
# (Optionnel car c'est le défaut, mais explicite pour Sonar)
RUN chmod -R 555 /app

# 5. Passage à l'utilisateur non-privilégié pour l'exécution
USER myuser

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]