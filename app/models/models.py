import sys
import os
sys.path.append(os.path.join(os.getcwd(),'app'))
import uuid
import datetime
from sqlalchemy import Column, create_engine, ForeignKey,UUID,String,DateTime
from core.db import Base,engine,SessionLocal
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship


class SmiSource(Base):

    __tablename__ = 'smi_source'

    id = Column(UUID(), primary_key=True, nullable=False)
    url = Column(String,nullable=False,unique=True)

    parsed_news = relationship('ParsedNews',back_populates='smi_source')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = str(uuid.uuid4())


class ParsedNews(Base):

    __tablename__ = 'parsed_news'

    id = Column(UUID(), primary_key=True, nullable=False)
    time_download = Column(DateTime,nullable = False)
    time_publish = Column(DateTime,nullable = False)
    title = Column(String,nullable = False)
    body = Column(String,nullable = False)
    source = Column(String,nullable = False)
    smi = Column(UUID(),ForeignKey('smi_source.id'))

    smi_source = relationship('SmiSource',back_populates='parsed_news')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = str(uuid.uuid4())
        self.time_download = datetime.datetime.now()


Base.metadata.create_all(engine)






