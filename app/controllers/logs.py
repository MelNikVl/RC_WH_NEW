from math import floor
from typing import List, Dict, Optional

from sqlalchemy.orm import Session

import fastapi
from app.controllers.front import templates
from app.controllers.materials import user_dependency
from app.utils.auth import AuthUtil
from db.db import get_db
from models.models import LogItem
from fastapi import Depends, Request, Response, status


class LogsController:
    # создание карточки
    @staticmethod
    async def logs(db: Session = Depends(get_db),
                   request: Request = None,
                   t: str = None, # jwt токен
                   p: int = 1, # пагинация
                   id: Optional[int] = "",
                   user: Optional[str] = "",
                   date_1: Optional[str] = ""
                   ):
        try:
            result = await AuthUtil.decode_jwt(t)
        except Exception as e:
            return fastapi.responses.RedirectResponse('/app/auth', status_code=status.HTTP_301_MOVED_PERMANENTLY)
        logs_from = None
        out: Dict = {}
        query = db.query(LogItem)

        # FILTERS
        out["id_filter"] = id
        out["user_filter"] = user
        out["date_filter"] = date_1
        out["token"] = t

        if id != "":
            query = query.filter(LogItem.passive_id == id)
        if user != "":
            query = query.filter(LogItem.user_id == user)
        if date_1 != "":
            query = query.filter(LogItem.date_time.contains(date_1))

        logs_from = query.all()
        # END_FILTERS

        items_number = 100
        page_count = floor(len(logs_from)/items_number)+1
        page = min(p, page_count)
        page = max(page, 1)
        start_index = page*items_number - items_number
        end_index = page*items_number

        out["items"] = logs_from[start_index:end_index]
        out["page_count"] = page_count
        out["current_page"] = page
        out["role"] = result["role"]

        return templates.TemplateResponse("logs.html", {"request": request, "data": out})
