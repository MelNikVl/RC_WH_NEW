from typing import List, Optional
from fastapi import Form
from pydantic import BaseModel


class MaterialCreateRequest(BaseModel):
    id: int
    category: str
    title: str
    description: str
    place: Optional[str]


# класс для формирования файла загрузки списка товаров на утиль
class InvoiceCreateRequest(BaseModel):
    data: List[List[str]]


class MaterialsListRequest(BaseModel):
    data: List[List[str]]


class MaterialGetRequest(BaseModel):
    id: int


class MaterialUpdateDescriptionRequest(BaseModel):
    id: int
    description: str


class MaterialDeleteRequest(BaseModel):
    id: int


class GeoLocationCreateRequest(BaseModel):
    material_id: int
    place: str
    client_mail: str
    status: str


class GeoLocationGetByIdRequest(BaseModel):
    material_id: int


class UserAuth(BaseModel):
    chat_id_from_tg: int
    username: str
    password: str
    # password: str = Field(
    #     ...,
    #     min_length=8,
    #     regex=r'^\d{10}$',
    #     description='описание пароля'
    # )
    is_admin: bool = False


class RepairCreateRequest(BaseModel):
    material_id: int = Form()
    problem: str = Form()
    customer: str = Form()


class RepairStopRequest(BaseModel):
    material_id: int
    solution: str
    customer: str
    place: str
    status: str

class RepairDetailsRequest(BaseModel):
    material_id: int
    details: str

class AccessoriesRequest(BaseModel):
    category: str
    title: str
    count: int
    place: str