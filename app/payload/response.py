# альтернативный формат даты
# from datetime import datetime
from typing import Optional
import datetime

from pydantic import BaseModel, validator


# отображение данных для карточек
class MaterialUploadResponse(BaseModel):
    id: int
    user_id: Optional[str]
    category: str
    title: str
    description: str
    date_time: datetime.date
    # альтернативный формат даты
    # date_time: datetime.datetime
    geolocation_id: Optional[int]

    # альтернативный формат даты
    # @validator('date_time')
    # def format_date(cls, date_time: datetime) -> str:
    #     return date_time.strftime("%m - %d - %Y")

    class Config:
        orm_mode = True


# отображение данных для перемещений
class GeoLocationUploadResponse(BaseModel):
    id: int
    material_id: int
    place: Optional[str]
    client_mail: str
    status: Optional[str]
    date_time: datetime.date

    class Config:
        orm_mode = True


class LogsUploadResponse(BaseModel):
    id: int
    kind_table: str
    user_id: int
    passive_id: int
    modified_cols: str
    values_of_change: str
    date_time: datetime.date

