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