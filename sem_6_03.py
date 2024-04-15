# Задание №3
# Создать API для управления списком задач.
# Каждая задача должна содержать поля "название",
# "описание" и "статус" (выполнена/не выполнена).
# API должен позволять выполнять CRUD операции с
# задачами.
from typing import List
from fastapi import FastAPI
from pydantic import BaseModel, Field
import databases
import sqlalchemy
import uvicorn

DATABASE_URL = "sqlite:///tasks3.db"  # создаем базу данных в корневой директории
database = databases.Database(DATABASE_URL)  # переменная из класса Database
metadata = sqlalchemy.MetaData()  # метаданные


tasks = sqlalchemy.Table(
    "tasks",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String(100)),
    sqlalchemy.Column("description", sqlalchemy.String(100)),
    sqlalchemy.Column("done", sqlalchemy.String(15)),
)
engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
metadata.create_all(engine)

app = FastAPI()

class TaskIn(BaseModel):
    title: str = Field(..., max_length=100)
    description: str = Field(..., max_length=100)
    done: str = Field(..., max_length=15)


class Task(TaskIn):
    id: int



@app.get("/create_table/{count}")
async def create_table(count: int):
    for i in range(count):
        query = tasks.insert().values(title=f'решить задачу номер {i+1}',
                                      description=f'задача на Пайтон {i+1}',
                                      done=f'не выполнена')
        await database.execute(query)
    return {"message": f"Сгенерировано {count} задач"}

@app.get("/tasks/", response_model=List[Task])
async def get_tasks():
    query = tasks.select()
    return await database.fetch_all(query)


@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(tasks_id: int):
    query = tasks.select().where(tasks.c.id == tasks_id)
    return await database.fetch_one(query)


@app.post("/tasks/", response_model=TaskIn)
async def create_task(task: TaskIn):
    query = tasks.insert().values(**task.model_dump())
    create_id = await database.execute(query)
    return await get_task(create_id)


@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(tasks_id: int, task: TaskIn):
    query = tasks.update().where(tasks.c.id == tasks_id).values(**task.model_dump())
    await database.execute(query)
    return await get_task(tasks_id)


@app.delete("/tasks/{task_id}")
async def delite_task(tasks_id: int):
    query = tasks.delete().where(tasks.c.id == tasks_id)
    await database.execute(query)
    return {'msg': 'Удалено'}

if __name__ == "__main__":
        uvicorn.run(app, host="127.0.0.1", port=8000)