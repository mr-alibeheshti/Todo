from fastapi import APIRouter,Depends,status,HTTPException
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext
from typing import Annotated
from sqlalchemy.orm import session
from database import LocalSession
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()
db_dependency = Annotated[session,Depends(get_db)]

bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated='auto')

def auth_user(username:str,password:str,db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password,user.hashed_password):
        return False
    return True
class CreateUserReq(BaseModel):
    username:str
    email:str
    first_name:str
    last_name:str
    password:str
    role:str
router = APIRouter()

@router.post("/signup/", status_code=status.HTTP_201_CREATED)
async def sign_up(db: db_dependency, usermode: CreateUserReq):
    try:
        create_user_model = Users(
            email=usermode.email,
            username=usermode.username,
            first_name=usermode.first_name,
            last_name=usermode.last_name,
            role=usermode.role,
            hashed_password=bcrypt_context.hash(usermode.password),
            is_active=True
        )
        db.add(create_user_model)
        db.commit()
        return create_user_model
    except Exception as e:
        db.rollback() 
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.post("/login")
async def login(form_data : Annotated[OAuth2PasswordRequestForm,Depends()],db:db_dependency):
    auth = auth_user(form_data.username,form_data.password,db)
    if not auth :
        return "Failed authentication"
    return "successfully authentication"