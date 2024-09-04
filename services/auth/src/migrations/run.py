import os
import sys
from argparse import Namespace
from pathlib import Path

from alembic import command
from alembic.config import Config

PROJECT_PATH = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_PATH))


class AlembicMigrator:
    def __init__(
        self,
        base_path: Path = PROJECT_PATH,
        project_folder: str = "",
        config_file: str = "alembic.ini",
        database_url: str | None = None,
    ) -> None:
        """
        Initializes the Alembic migrator.
        """
        self.base_path = base_path
        self.config_file = config_file
        self.project_name = project_folder
        self.database_url = database_url

    def _get_config(self) -> Config:
        """
        Gets the Alembic configuration.
        """
        cmd_options = Namespace(
            config=self.config_file, name="alembic", pg_dsn=self.database_url, raiseerr=False, x=None
        )
        if not os.path.isabs(cmd_options.config):
            cmd_options.config = os.path.join(self.base_path, self.project_name, cmd_options.config)

        config = Config(file_=cmd_options.config, ini_section=cmd_options.name, cmd_opts=cmd_options)

        alembic_location = config.get_main_option("script_location")
        if not os.path.isabs(alembic_location):
            config.set_main_option("script_location", os.path.join(self.base_path, self.project_name, alembic_location))

        if self.database_url:
            config.set_main_option("sqlalchemy.url", self.database_url)

        return config

    def upgrade(self) -> None:
        """
        Executes the `upgrade` command for Alembic.
        """
        config = self._get_config()
        command.upgrade(config, "head")


if __name__ == "__main__":
    from core.settings import settings

    dsn = settings.pg.dsn
    pg_dsn_with_fallback = f"{dsn}?async_fallback=True"
    project_name = settings.project_root
    migrator = AlembicMigrator(project_folder=project_name, database_url=pg_dsn_with_fallback)
    migrator.upgrade()
