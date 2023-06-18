from datetime import datetime
from typing import List
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean, TIMESTAMP


# здесь находятся модели для создания таблиц в базе данных - каждый класс - отдельная таблица

# вид базы данных
Base = declarative_base()

class User(Base):
    __tablename__ = "user"

    id: int = Column(Integer, primary_key=True, index=True)
    chat_id: int = Column(Integer)
    username: str = Column(String)
    password: str = Column(String)
    is_admin: bool = Column(Boolean, default=False)


class Material(Base):
    __tablename__ = "material"

    id: int = Column(Integer, primary_key=True, index=True)
    user_id: int = Column(Integer, ForeignKey('user.id'))
    category: str = Column(String)
    title: str = Column(String)
    description: str = Column(String)
    date_time: datetime = Column(DateTime)
    geolocation_id: int = Column(Integer, ForeignKey('geolocation.id'))

class Trash(Base):
    __tablename__ = "trash"

    id: int = Column(Integer, primary_key=True, index=True)
    user_id: int = Column(Integer, ForeignKey('user.id'))
    category: str = Column(String)
    title: str = Column(String)
    description: str = Column(String)
    date_time: datetime = Column(DateTime)
    geolocation_id: int = Column(Integer, ForeignKey('geolocation.id'))


class GeoLocation(Base):
    __tablename__ = "geolocation"

    id: int = Column(Integer, primary_key=True, index=True)
    material_id: int = Column(Integer, ForeignKey('material.id'))
    place: str = Column(String)
    client_mail: str = Column(String)
    status: str = Column(String)
    date_time: datetime = Column(DateTime)


class LogItem(Base):
    __tablename__ = "log"

    id: int = Column(Integer, primary_key=True, index=True)
    kind_table: str = Column(String)
    user_id: int = Column(Integer)
    passive_id: int = Column(Integer)
    modified_cols: str = Column(String)
    values_of_change: str = Column(String)
    date_time: str = Column(String)
