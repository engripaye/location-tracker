from sqlalchemy import (
Column,
Integer,
String,
Float,
DateTime,
ForeignKey,
Boolean
)

from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    password_hash = Column(String)


