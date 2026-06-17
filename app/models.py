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
