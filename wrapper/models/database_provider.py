import os

from wrapper.utils.config_loader import ConfigLoader
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import Session, sessionmaker


class DatabaseProvider:
    _instance = None

    def __init__(self) -> None:
        mysql_config = ConfigLoader.load(os.getenv("CONFIG_FILE"))['mysqlConfig']

        # MySQL Connection String
        self.engine = create_engine(
            f"mysql+mysqlconnector://{mysql_config['user']}:{mysql_config['password']}"
            f"@{mysql_config['host']}:{mysql_config['port']}/{mysql_config['database']}", echo=True)
        _session_maker = sessionmaker(bind=self.engine)
        self.session: Session = _session_maker()

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
