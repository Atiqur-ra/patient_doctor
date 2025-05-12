from database import Base
from sqlalchemy import Column, String, Integer


class DocumentIndex(Base):
    __tablename__ = "document_indices"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer)
    chat_name = Column(String, unique=True)
    index_name = Column(String)