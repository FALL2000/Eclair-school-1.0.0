import bcrypt


def hash_password(password: str) -> str:
    """Hache le mot de passe en clair en utilisant bcrypt."""
    # 1. Convertir le texte clair en bytes
    password_bytes = password.encode('utf-8')

    # 2. Générer un sel (salt)
    salt = bcrypt.gensalt()

    # 3. Hacher le mot de passe
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)

    # 4. Retourner une string pour le stockage en DB (format $2b$...)
    return hashed_bytes.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie si le mot de passe correspond au hachage stocké."""
    try:
        # Convertir les deux entrées en bytes
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')

        # Comparer de manière sécurisée (contre les attaques temporelles)
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        # En cas de format de hash invalide ou erreur d'encodage
        return False
