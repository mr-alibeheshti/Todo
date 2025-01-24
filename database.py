from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
DATABASE_URL = "sqlite:///./todos.db"
DATABASE_URL_2 = "sqlite:///./todos.db"
engine = create_engine(DATABASE_URL,connect_args={'check_same_thread':False})
LocalSession = sessionmaker(autoflush=False,autocommit=False,bind=engine)
Base = declarative_base()