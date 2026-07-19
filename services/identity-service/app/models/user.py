import datetime
import uuid
from sqlalchemy import Column, String, DateTime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False) # 'CONDUCTOR' or 'PASAJERO'
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
