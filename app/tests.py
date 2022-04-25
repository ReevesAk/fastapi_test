import asyncio
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from main import app
from models import Tasks, Tasks

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
    response = client.post("/tasks", json={"title": "Produce Juice"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["title"] == "Produce Juice"
    assert "id" in data
    task_id = data["id"]

    async def get_task_by_db():
        task = await Tasks.get(id=task_id)
        return task

    task_obj = event_loop.run_until_complete(get_task_by_db())
    assert task_obj.id == task_id

def test_get_task(client: TestClient, event_loop: asyncio.AbstractEventLoop):
    response = client.get("/tasks", json={"title": "Produce"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["title"] == "Produce"
    assert "id" in data
    task_id = data["id"]

    async def get_task_by_db():
        task = await Tasks.get(id=task_id)
        return task

    task_obj = event_loop.run_until_complete(get_task_by_db())
    assert task_obj.id == task_id    


def test_update_task(client: TestClient, event_loop: asyncio.AbstractEventLoop):
    response = client.put("/tasks", json={"title": "Produce juice",
                                           "description": "Get the fruit and juice it"
                                           "is_completed: True"})


    assert response.status_code == 200, response.text
    data = response.json()
    assert data["title"] == "Produce juice"
    assert "id" in data
    task_id = data["id"]

    async def get_task_by_db():
            task = await Tasks.get(id=task_id)
            return task

    task_obj = event_loop.run_until_complete(get_task_by_db())
    assert task_obj.id == task_id


def test_delete_task(client: TestClient, event_loop: asyncio.AbstractEventLoop):
    response = client.delete("/tasks", json={"title": "Produce juice",
                                           "description": "Get the fruit and juice it"
                                           "is_completed: True"})


    assert response.status_code == 404, response.text
    data = response.json()
    assert data["title"] == "Not Found"