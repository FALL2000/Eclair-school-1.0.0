import pkgutil
import importlib
import os
import sys

# 1. Le chemin absolu de ce dossier (models/)
package_path = os.path.dirname(__file__)

# 2. On itère sur tous les sous-dossiers de models/
for dirpath, dirnames, filenames in os.walk(package_path):
    # On ignore les dossiers spéciaux
    dirnames[:] = [d for d in dirnames if d not in ('__pycache__', 'init')]

    # On calcule le chemin relatif par rapport au dossier PARENT de 'models'
    # Pour que le pkg_name commence par 'models'
    rel_path = os.path.relpath(dirpath, os.path.dirname(package_path))

    # On remplace les slashs par des points (ex: models.administration)
    pkg_name = rel_path.replace(os.sep, ".")

    # Découvrir et importer les modules .py dans ce dossier
    for _, module_name, is_pkg in pkgutil.iter_modules([dirpath]):
        if not is_pkg:
            full_module_name = f"{pkg_name}.{module_name}"
            try:
                # Importation dynamique
                importlib.import_module(full_module_name)
            except Exception as e:
                print(f"Erreur lors de l'import de {full_module_name}: {e}")
