#!/bin/bash

# Fonction pour attendre que la DB soit prête
wait_for_db() {
  echo "Attente de la base de données sur $DB_HOST:$DB_PORT..."
  # On essaie de se connecter pendant 30 secondes
  for i in {1..30}; do
    # On utilise python pour tester la connexion réseau
    if python -c "import socket; s = socket.socket(); s.connect(('$DB_HOST', int('$DB_PORT')))" >/dev/null 2>&1; then
      echo "La base de données est prête !"
      return 0
    fi
    echo "Base de données non disponible (essai $i/30)..."
    sleep 2
  done
  echo "Erreur : La base de données n'a pas démarré à temps."
  exit 1
}

# 1. Attendre la DB
wait_for_db

# 2. Lancer les migrations
echo "Application des migrations Alembic..."
alembic upgrade head

# 3. Démarrer l'application
echo "Démarrage de FastAPI..."
exec uvicorn main:app --host 0.0.0.0 --port 8000