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
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    password_hash = Column(String)

class TrackingSession(Base):
    __tablename__ = 'tracking_sessions'
    id = Column(Integer, primary_key=True)

    owner_id = Column(Integer, ForeignKey('user.id'))

    share_token = Column(String, unique=True)

    active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.now())


class LocationPoint(Base):
    __tablename__ = 'location_points'
    id = Column(Integer, primary_key=True)

    session_id = Column(Integer, ForeignKey('tracking_sessions.id'))

    latitude = Column(Float)
    longitude = Column(Float)

    accuracy = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)
