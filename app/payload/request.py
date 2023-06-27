from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class MaterialCreateRequest(BaseModel):
    id: int
    # user_id: int
    category: str
    title: str
    description: str
    place: Optional[str]
    # client_mail: Optional[str]


# класс для формирования файла загрузки списка товаров на утиль
class InvoiceCreateRequest(BaseModel):
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
    material_id: int
    problem: str
    customer: str


class RepairStopRequest(BaseModel):
    material_id: int
    decision: str
    customer: str
    dept: str
    status: str

class RepairDetailsRequest(BaseModel):
    material_id: str
    details: str