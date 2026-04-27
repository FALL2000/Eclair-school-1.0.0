from typing import Generic, TypeVar, Type, List, Optional, Any
from sqlalchemy import and_
from sqlmodel import Session, delete, insert, select, func, update

# T représente le modèle SQLModel (ex: Eleve, User)
T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], session: Session):
        self.model = model
        self.session = session

    def findOne(self, id: Any) -> Optional[T]:
        """Récupère un élément par son ID (clé primaire)."""
        return self.session.get(self.model, id)

    def findAll(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[T]:
        """Récupère tous les éléments avec pagination optionnelle."""
        statement = select(self.model)
        if offset is not None:
            statement = statement.offset(offset)
        if limit is not None:
            statement = statement.limit(limit)
        return self.session.exec(statement).all()

    def findBy(self, **kwargs) -> List[T]:
        """
        Recherche dynamique. 
        Exemple d'usage : repo.findBy(email="test@test.com", is_active=True)
        """
        statement = select(self.model)
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                statement = statement.where(getattr(self.model, key) == value)
        return self.session.exec(statement).all()

    def save(self, instance: T) -> T:
        """Create ou Update. SQLModel gère l'upsert via add()."""
        self.session.add(instance)
        # On flush pour synchroniser l'ID sans commiter la transaction
        self.session.flush()
        self.session.refresh(instance)
        return instance

    def deleteOne(self, id: Any) -> bool:
        """Supprime un élément par son ID."""
        obj = self.findOne(id)
        if obj:
            self.session.delete(obj)
            self.session.flush()
            return True
        return False

    def InsertMany(self, data_list: List[dict]) -> None:
        """
        INSERTION en masse.
        data_list: Liste de dictionnaires ex: [{'name': 'A', 'email': 'a@a.com'}, ...]
        """
        if not data_list:
            return

        statement = insert(self.model).values(data_list)
        self.session.exec(statement)
        self.session.flush()

    def updateMany(self, filters: dict, updates: dict) -> int:
        """
        MODIFICATION en masse.
        Exemple: repo.updateMany({'classe_id': 1}, {'statut': 'DIPLOME'})
        Retourne le nombre de lignes modifiées.
        """
        if not updates:
            return 0

        # Construction dynamique des filtres WHERE
        where_clauses = [getattr(self.model, k) ==
                         v for k, v in filters.items()]

        statement = (
            update(self.model)
            .where(and_(*where_clauses))
            .values(updates)
            # Garde la session Python à jour
            .execution_options(synchronize_session="fetch")
        )

        result = self.session.exec(statement)
        self.session.flush()
        return result.rowcount

    def deleteMany(self, ids: List[Any]) -> int:
        """
        SUPPRESSION en masse par IDs.
        """
        if not ids:
            return 0

        statement = (
            delete(self.model)
            .where(self.model.id.in_(ids))
            .execution_options(synchronize_session="fetch")
        )

        result = self.session.exec(statement)
        self.session.flush()
        return result.rowcount

    def __getattr__(self, name: str):
        """
        Magie Python pour gérer le findByEmail, findByName, etc.
        Si la méthode n'existe pas, on vérifie si elle commence par 'findBy'.
        """
        if name.startswith("findBy"):
            # Récupère 'Email' de 'findByEmail' -> 'email'
            field_name = name[6:].lower()

            def wrapper(value):
                return self.findBy(**{field_name: value})
            return wrapper
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'")
