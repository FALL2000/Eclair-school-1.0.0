from sqlmodel import create_engine, Session, SQLModel

from config.settings import get_settings

settings = get_settings()


DATABASE_URL = (
    settings.db_engine_string
    + "://"
    + settings.db_user
    + ":"
    + settings.db_password
    + "@"
    + settings.db_host
    + ":"
    + str(settings.db_port)
    + "/"
    + settings.db_name
)

if not settings.app_env or settings.app_env == "test":
    DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(DATABASE_URL, pool_pre_ping=True,
                       pool_recycle=280, echo=True)
