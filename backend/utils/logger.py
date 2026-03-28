import os
import logging
from logging.handlers import RotatingFileHandler

__mega_octet_log_size__ = 10
max_bytes = __mega_octet_log_size__ * 1024 * 1024
uvicorn_log_max_bytes = 10 * __mega_octet_log_size__ * 1024 * 1024

log_directory = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "logs"
)

if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Création des gestionnaires de fichiers pour chaque niveau de log avec les chemins appropriés
info_handler = RotatingFileHandler(
    os.path.join(log_directory, "info.log"),
    maxBytes=max_bytes,  # Limite de taille de fichier de 10 Mo
    backupCount=5,  # Garder les 5 derniers fichiers de log
    encoding='utf-8'
)
info_handler.setLevel(logging.INFO)

warning_handler = RotatingFileHandler(
    os.path.join(log_directory, "warning.log"),
    maxBytes=max_bytes,  # Limite de taille de fichier de 10 Mo
    backupCount=5,  # Garder les 5 derniers fichiers de log
    encoding='utf-8'
)
warning_handler.setLevel(logging.WARNING)

error_handler = RotatingFileHandler(
    os.path.join(log_directory, "error.log"),
    maxBytes=max_bytes,  # Limite de taille de fichier de 10 Mo
    backupCount=5,  # Garder les 5 derniers fichiers de log
    encoding='utf-8'
)
error_handler.setLevel(logging.ERROR)

# Création d'un format commun pour les logs
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Appliquer le format à chaque gestionnaire
info_handler.setFormatter(formatter)
warning_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(
    logging.DEBUG
)  # Niveau global minimum, ici DEBUG pour capter tous les logs

# Ajouter les gestionnaires au logger (une seule fois par processus)
if not logger.handlers:
    logger.addHandler(info_handler)
    logger.addHandler(warning_handler)
    logger.addHandler(error_handler)

# Évite la double sortie si le root logger a aussi des handlers (ex. uvicorn).
logger.propagate = False


def get_logger():
    return logger


def get_log_directory():
    return log_directory
