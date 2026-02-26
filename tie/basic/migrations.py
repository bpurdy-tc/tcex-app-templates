"""ThreatConnect API Service App"""

from core.service.migration_service import MigrationService

# from core.tcvf.service.sqlite_migration_service import SQLiteMigrationModel


class Migrations:
    """API Service App"""

    def __init__(self, tcex, json_db, settings):
        """Initialize class properties."""
        self.migration_service = MigrationService(tcex, tcex.log, json_db, settings)
        self.register_sqlite_migrations()
        self.register_migrations()

    def register_sqlite_migrations(self):
        """Register custom sqlite migrations."""
        # This function is optional.

        # Register all sqlite -> json_db migrations. It is expected that the
        # sqlite db structure is the same as the json_db

        # Example:
        # sqlite_migrations = [
        # SQLiteMigrationModel(
        #     table_name='custom_table',
        #     model=CustomRequestModel,
        # ),
        # SQLiteMigrationModel(
        #     table_name='custom_table_2',
        #     model=CustomRequestModel2,
        #     query='SELECT * FROM custom_table_2 order by date_queued desc',
        # ),
        # SQLiteMigrationModel(
        #     table_name='custom_table_3',
        #     model=CustomRequestModel3,
        #     row_callback=self.custom_table_3_row_transform,
        # ),
        # SQLiteMigrationModel(
        #     table_name='custom_migration_table',
        #     model=CustomMigrationTable',
        #     post_migration_callback=self.post_migration_callback,
        # )
        # ]
        # for migration in sqlite_migrations:
        #     self.migration_service.sql_lite_migration.register_model_migration(migration)

        # row_callback is a list of functions that take a row (dict) and return a dict or None
        # post_migration_callback is a function that takes a list of model objects and returns
        # a list of models

        return

    def register_migrations(self):
        """Register all migrations."""
        # Register all migrations from one version using the json db to another

        # Example:
        # self.migration_service.register_migration('1.0.0', self._1_0_0)

        # self._1_0_0 is a method that takes the version and the json db, may
        # still need to think through this a bit more.
        return
