from sqlalchemy import create_engine,MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase

# from core.config import settings


# DATABASE_URL = 'clickhouse://default:123@localhost:8123/default'
DATABASE_URL = f'postgresql://ascar:1@localhost:5432/pars'


engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, bind=engine)



class Base(DeclarativeBase):
    pass


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()