from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean, Float
from enum import Enum

# здесь находятся модели для создания таблиц в базе данных - каждый класс - отдельная таблица

# вид базы данных
Base = declarative_base()


class GEO_TYPE(Enum):
    request = 0
    movement = 1


class User(Base):
    __tablename__ = "user"

    id: int = Column(Integer, primary_key=True, index=True)
    chat_id: int = Column(Integer)
    username: str = Column(String)
    password: str = Column(String)
    is_admin: bool = Column(Boolean, default=False)


class Material(Base):
    __tablename__ = "material"

    id: str = Column(String, primary_key=True, index=True)
    user_id: int = Column(Integer, ForeignKey('user.id'))
    category: str = Column(String)
    title: str = Column(String)
    description: str = Column(String)
    date_time: datetime = Column(DateTime)
    geolocation_id: int = Column(Integer, ForeignKey('geolocation.id'))


class Trash(Base):
    __tablename__ = "trash"

    id: int = Column(Integer, primary_key=True, index=True)
    user_id: int = Column(Integer)
    material_id: int = Column(Integer)
    category: str = Column(String)
    title: str = Column(String)
    description: str = Column(String)
    moving: str = Column(String)
    repairs: str = Column(String)
    date_time: str = Column(String)
    folder_name: str = Column(String)
    trash_unique_id: str = Column(String)


class GeoLocation(Base):
    __tablename__ = "geolocation"

    id: int = Column(Integer, primary_key=True, index=True)
    material_id: str = Column(String, ForeignKey('material.id'))
    place: str = Column(String)
    client_mail: str = Column(String)
    status: str = Column(String, nullable=True)
    initiator: str = Column(String, nullable=True)
    date_time: datetime = Column(DateTime)
    geo_type: int = Column(Integer)
    comment: str = Column(String, default="")

class LogItem(Base):
    __tablename__ = "log"

    id: int = Column(Integer, primary_key=True, index=True)
    kind_table: str = Column(String)
    user_id: int = Column(Integer)
    passive_id: int = Column(Integer)
    modified_cols: str = Column(String)
    values_of_change: str = Column(String)
    date_time: str = Column(String)


class Repair(Base):
    __tablename__ = "repair"

    id: int = Column(Integer, primary_key=True, index=True)
    material_id: str = Column(String)
    responsible_it_dept_user: str = Column(String)
    problem_description: str = Column(String)
    user_whose_technique: str = Column(String)
    date_time: str = Column(String)
    repair_number: int = Column(Integer)
    repair_status: bool = Column(Boolean)
    repair_unique_id: str = Column(String)


class Accessories(Base):
    __tablename__ = "accessories"

    id: int = Column(Integer, primary_key=True, index=True)
    category: str = Column(String)
    title: int = Column(Integer)
    count: str = Column(String)
    responsible: str = Column(String)
    place: str = Column(String)
    date_time: datetime = Column(DateTime)


class Notifications(Base):
    __tablename__ = "notifications"

    id: int = Column(Integer, primary_key=True, index=True)
    category: str = Column(String)
    user: str = Column(String)
    read: bool = Column(Boolean,  unique=False, default=False)
    unique_code: str = Column(String)
    date_time: datetime = Column(DateTime)
    material_id: str = Column(String)
    geolocation_id: int = Column(Integer, ForeignKey("geolocation.id"), nullable=True, default=None)


class Comment(Base):
    __tablename__ = "comments"
    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    material_id = Column(String, ForeignKey('material.id'))
    user_id: int = Column(Integer, ForeignKey('user.id'))
    user_name_1: str = Column(String(30), nullable=True)
    text: str = Column(String(100))
    date_time: datetime = Column(DateTime)


class Raw_1c(Base):
    __tablename__ = "raw_1c"
    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    material_id = Column(String, ForeignKey('material.id'))
    name_ru: str = Column(String, nullable=True)
    name_en: str = Column(String, nullable=True)
    full_name: str = Column(String, nullable=True)
    date_time: datetime = Column(DateTime)
    organization: str = Column(String, default="")
    cost: float = Column(Float, default=0.00)
    cur_dept: str = Column(String, nullable=True)
    cur_person: str = Column(String, nullable=True)

