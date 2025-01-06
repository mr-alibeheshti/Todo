from turtle import title
from fastapi import FastAPI,Depends,HTTPException,status,Path
from typing import Annotated
from database import engine
from pydantic import BaseModel, Field
from database import LocalSession
from sqlalchemy.orm import session
import models
from models import Todos
app = FastAPI()

models.Base.metadata.create_all(bind=engine)
def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()
db_dependency = Annotated[session,Depends(get_db)]

class TodoRequest(BaseModel):
    title:str = Field(min_length=3)
    description:str = Field(min_length=3,max_length=100)
    priority:int = Field(gt=0,lt=6)
    complete:bool = Field(default=False)

@app.get("/",status_code=status.HTTP_200_OK)
async def read_all(db:db_dependency):
    return db.query(Todos).all()

@app.get("/todo/{todo_id}",status_code=status.HTTP_200_OK)
async def read_todo(db:db_dependency,todo_id:int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404,detail=f"Todo with id {todo_id} not found")

@app.post("/",status_code=status.HTTP_201_CREATED)
async def create_todo(todo:TodoRequest,db:db_dependency):
    todo_model = Todos(**todo.dict())
    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)
    return todo_model

@app.put("/todo/{todo_id}",status_code=status.HTTP_200_OK)
async def update_todo(db:db_dependency,todo:TodoRequest,todo_id:int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404,detail=f"Todo with id {todo_id} not found")
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete
    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)
    return todo_model

@app.delete("/todo/{todo_id}",status_code=status.HTTP_200_OK)
async def delete_todo(db:db_dependency,todo_id:int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404,detail=f"Todo with id {todo_id} not found")
    db.delete(todo_model)
    db.commit()
    return {"message":"Todo deleted successfully"}