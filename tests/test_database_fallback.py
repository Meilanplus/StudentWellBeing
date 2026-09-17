import unittest
from unittest.mock import patch

from sqlalchemy.exc import OperationalError

from app import database


class DatabaseFallbackTests(unittest.TestCase):
    def test_dev_mode_falls_back_to_sqlite_when_postgres_timeout(self):
        with patch.object(database.settings, "app_env", "development"), patch.object(
            database.settings, "database_url", "postgresql+psycopg://user:pass@badhost:5432/example"
        ), patch("app.database.create_engine", side_effect=OperationalError("connection timeout expired", None, None)):
            result = database.resolve_database_url()

        self.assertTrue(result.startswith("sqlite:///"))
        self.assertIn("studentwellbeing.db", result)


if __name__ == "__main__":
    unittest.main()
