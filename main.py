from fastapi import FastAPI,Depends
from typing import Annotated
from database import engine
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
@app.get("/")
async def read_all(db:db_dependency):
    return db.query(Todos).all()