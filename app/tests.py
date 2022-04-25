import asyncio
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from main import app
from models import Tasks

from tortoise.contrib.test import finalizer, initializer


@pytest.fixture(scope="module")
def client() -> Generator:
    initializer(["models"])
    with TestClient(app) as c:
        yield c
    finalizer()


@pytest.fixture(scope="module")
def event_loop(client: TestClient) -> Generator:
    yield client.task.get_loop()


def test_create_task(client: TestClient, event_loop: asyncio.AbstractEventLoop):  # nosec
    response = client.post("/tasks", json={"username": "admin"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == "admin"
    assert "id" in data
    user_id = data["id"]

    async def get_user_by_db():
        user = await Tasks.get(id=user_id)
        return user

    user_obj = event_loop.run_until_complete(get_user_by_db())
    assert user_obj.id == user_id

def test_get_task(client: TestClient, event_loop: asyncio.AbstractEventLoop):  # nosec
    response = client.get("/tasks", json={"username": "admin"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == "admin"
    assert "id" in data
    user_id = data["id"]

    async def get_user_by_db():
        user = await Tasks.get(id=user_id)
        return user

    user_obj = event_loop.run_until_complete(get_user_by_db())
    assert user_obj.id == user_id    