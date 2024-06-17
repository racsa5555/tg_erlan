from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from models.models import ParsedNews,SmiSource
from core.db import SessionLocal

def create_news(db: Session,news:ParsedNews):
    db.add(news)
    db.commit()
    db.refresh(news)
    return news

def get_or_create_smi_source(url:str):
    db = SessionLocal()
    try:
        smi_source = db.execute(select(SmiSource).where(SmiSource.url == url)).scalar_one()
    except NoResultFound:
        smi_source = SmiSource(url=url)
        db.add(smi_source)
        db.commit()
        db.refresh(smi_source)
    db.close()
    return smi_source
