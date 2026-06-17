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

    class TrackingSession(Base):
        __tablename__ = 'tracking_session'
        id = Column(Integer, primary_key=True)

        owner_id = Column(Integer, ForeignKey('user.id'))

        share_token = Column(String, unique=True)

        active = Column(Boolean, default=True)
