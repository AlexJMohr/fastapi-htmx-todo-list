import itertools
from typing import Annotated

from fastapi import FastAPI, Request, Form, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

id_iter = itertools.count(1)
TODOS = [
    {"id": next(id_iter), "text": "Do something", "done": True},
    {"id": next(id_iter), "text": "Do something else", "done": False},
]


@app.get("/")
async def index(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("index.html", context)


@app.get("/todos")
async def todos(request: Request):
    context = {"request": request, "todos": TODOS}
    return templates.TemplateResponse("todos.html", context)


@app.post("/todos")
async def create(request: Request, text: Annotated[str, Form()]):
    todo = {"id": next(id_iter), "text": text, "done": False}
    TODOS.append(todo)
    context = {"request": request, "todo": todo}
    response = templates.TemplateResponse("todo.html", context)
    response.headers["HX-Trigger"] = "todo-updated"
    return response


@app.post("/todos/{id}")
async def update(request: Request, id: int, done: bool = Form(False)):
    todo = next(todo for todo in TODOS if todo["id"] == id)
    todo["done"] = done
    context = {"request": request, "todo": todo}
    response = templates.TemplateResponse("todo.html", context)
    response.headers["HX-Trigger"] = "todo-updated"
    return response


@app.delete("/todos/{id}")
async def delete(request: Request, id: int):
    todo = next(todo for todo in TODOS if todo["id"] == id)
    TODOS.remove(todo)
    response = Response(status_code=200)
    response.headers["HX-Trigger"] = "todo-updated"
    return response


@app.get("/completed")
async def completed(request: Request):
    done_count = sum(1 for todo in TODOS if todo["done"])
    context = {"request": request, "todos": TODOS, "done_count": done_count}
    return templates.TemplateResponse("completed.html", context)
