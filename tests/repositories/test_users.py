import pytest
import unittest
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.repositories.users import SqlUserRepository
from src.schemas.users import CreateUser, ViewUser
from src.storages.sql import SQLAlchemyStorage


class TestUsers(unittest.IsolatedAsyncioTestCase):
    @pytest.fixture(scope="package", autouse=True)
    def _set_settings(self):
        self.settings = settings

    @pytest.fixture(scope="package", autouse=True)
    def _set_storage(self):
        _storage = SQLAlchemyStorage.from_url(self.settings.DB_URL.get_secret_value())
        self.storage = _storage

    @pytest.fixture(scope="package", autouse=True)
    def repository(self):
        _repository = SqlUserRepository(self.storage)
        self.repository = _repository

    @pytest.fixture(autouse=True)
    async def setup(self):
        from sqlalchemy.sql import text

        # Clear all data from the database before each test
        async with self.storage.create_session() as session:
            session: AsyncSession
            q = text("DROP SCHEMA public CASCADE;" "CREATE SCHEMA public;")
            await session.execute(q)
        # Create the necessary tables before each test
        await self.storage.create_all()
        yield
        # Close the database connection after each test
        await self.storage.close_connection()

    @pytest.mark.asyncio
    async def test_create_if_not_exists(self):
        user_schema = CreateUser(email="test@innopolis.university", name="Test User")
        user = await self.repository.create_user_if_not_exists(user_schema)
        self.assertIsNotNone(user)
        self.assertIsInstance(user, ViewUser)
        self.assertIsNotNone(user.id)
        self.assertEqual(user.email, user_schema.email)
        self.assertEqual(user.name, user_schema.name)
