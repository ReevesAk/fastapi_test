import uvicorn
from typing import List

from fastapi import FastAPI, HTTPException
from . models import Task_Pydantic, TaskIn_Pydantic, Tasks
from pydantic import BaseModel

from tortoise.contrib.fastapi import HTTPNotFoundError, register_tortoise

app = FastAPI(title="Tortoise ORM FastAPI Task example")


class Status(BaseModel):
    message: str


@app.get("/")
async def hello_world():
    return {'hello':'world'}


@app.get("/tasks", response_model=List[Task_Pydantic])
async def get_tasks():
    return await TaskIn_Pydantic.from_queryset(Tasks.all())


@app.post("/tasks", response_model=Task_Pydantic)
async def create_single_task(user: TaskIn_Pydantic):
    task_obj = await Tasks.create(**user.dict(exclude_unset=True))
    return await Task_Pydantic.from_tortoise_orm(task_obj)


@app.post("/tasks", response_model=Task_Pydantic)
async def create_multiple_task(user: TaskIn_Pydantic):
    task_obj = []
    new_obj = await Tasks.create(**user.dict(exclude_unset=True))
    return await Task_Pydantic.from_tortoise_orm(task_obj.append(new_obj))


@app.get(
    "/task/{task_id}", response_model=Task_Pydantic, responses={404: {"model": HTTPNotFoundError}}
)
async def get_single_task(user_id: int):
    return await TaskIn_Pydantic.from_queryset_single(Tasks.get(id=user_id))


@app.put(
    "/task/{user_id}", response_model=Task_Pydantic, responses={404: {"model": HTTPNotFoundError}}
)
async def update_task(user_id: int, user: TaskIn_Pydantic):
    await Tasks.filter(id=user_id).update(**user.dict(exclude_unset=True))
    return await Task_Pydantic.from_queryset_single(Tasks.get(id=user_id))


@app.delete("/task/{task_id}", response_model=Status, responses={404: {"model": HTTPNotFoundError}})
async def delete_single_task(user_id: int):
    deleted_count = await Tasks.filter(id=user_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"Task {user_id} not found")
    return Status(message=f"Deleted task {user_id}")


@app.delete("/tasks", response_model=Status, responses={404: {"model": HTTPNotFoundError}}) 
async def delete_all_tasks():
    all_tasks = await Task_Pydantic.from_queryset(Tasks.all())
    for del_task in all_tasks:
        del_task.delete()
    return Status(message="All tasks deleted")


register_tortoise(
    app,
    db_url="postgres://reeves:password@localhost/fastapi_db",
    modules={"models": ["app.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)