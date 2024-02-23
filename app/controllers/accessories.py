import datetime, fastapi
from typing import Dict
from fastapi import Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.payload.request import AccessoriesRequest, NewAccLocation
from starlette import status
from app.utils.utils import response
from app.controllers.front import templates
from app.utils.auth import AuthUtil, user_dependency
from db.db import get_db
from models.models import LogItem, Accessories


class AccessoriesController:

    @staticmethod
    async def accessories_page(db: Session = Depends(get_db),
                               request: Request = None,
                               t: str = None  # jwt токен
                               ):
        # проверка токена на валидность и если он не вализный - переадресация на авторизацию
        try:
            result = await AuthUtil.decode_jwt(t)
        except Exception as e:
            return fastapi.responses.RedirectResponse('/app/auth', status_code=status.HTTP_301_MOVED_PERMANENTLY)

        out: Dict = {}

        top_info = db.query(LogItem).filter(LogItem.kind_table == "Комплектующие"). \
            filter(LogItem.passive_id == "выдача").order_by(LogItem.id.desc()).limit(5).all()

        accessories = db.query(Accessories).all()
        for item in accessories:
            item.date_time = item.date_time.strftime("%Y-%m-%d %H:%M")

        out[0] = accessories
        out["token"] = t
        out["count_accessories"] = len(accessories)
        out["top_info"] = top_info
        out["role"] = result["role"]
        result = await AuthUtil.decode_jwt(t)
        out["username"] = result["username"]

        return templates.TemplateResponse("accessories_page.html", {"request": request, "data": out})

    @staticmethod
    async def create(body: AccessoriesRequest,
                     user: user_dependency,
                     db: Session = Depends(get_db),
                     ):

        accessories = Accessories(category=body.category,
                                  title=body.title,
                                  count=body.count,
                                  responsible=user.get("username"),
                                  place=body.place,
                                  date_time=datetime.datetime.now()
                                  )

        new_acc_event = LogItem(kind_table="Комплектующие",
                                user_id=user["username"],
                                passive_id=body.title,
                                modified_cols="добавление комплектующих",
                                values_of_change=f'категория: {body.category},'
                                                 f' количество {body.count}',
                                date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                )
        db.add(new_acc_event)
        db.add(accessories)
        db.commit()

        return response(data="комплектующие добавлены", status=True)

    @staticmethod
    async def change_count(title,
                           count,
                           resp_user: str,
                           user: user_dependency,
                           db: Session = Depends(get_db),
                           ):
        repair = db.query(Accessories).filter(Accessories.title == title).first()
        if repair.count == 0:
            return response(data="этих комплектующих нет", status=False)
        else:
            repair.count = int(repair.count) - int(count)

            new_acc_event = LogItem(kind_table="Комплектующие",
                                    user_id=user["username"],
                                    passive_id="выдача",
                                    modified_cols=f'новое количество: {repair.count}',
                                    values_of_change=f'{user["username"]} выдал пользователю {resp_user} '
                                                     f'{title} в количестве {count} шт, осталось {repair.count}',
                                    date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    )
            db.add(new_acc_event)
            db.commit()

            return response(data="комплектующие отданы", status=True)

    @staticmethod
    async def add_accessories(title,
                              count,
                              user: user_dependency,
                              db: Session = Depends(get_db),
                              ):
        repair = db.query(Accessories).filter(Accessories.title == title).first()
        repair.count = repair.count + int(count)

        new_acc_event = LogItem(kind_table="Комплектующие",
                                user_id=user["username"],
                                passive_id=title,
                                modified_cols="изменения количества комплектующих",
                                values_of_change=f'новое количество: {count}',
                                date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                )
        db.add(new_acc_event)
        db.commit()

        return response(data="комплектующие добавлены", status=True)

    @staticmethod
    async def change_location_acc(body: NewAccLocation,
                                  user: user_dependency,
                                  db: Session = Depends(get_db)
                                  ):
        acc_id = db.query(Accessories).filter(Accessories.id == body.id).first()
        if not acc_id:
            raise HTTPException(status_code=404, detail="Категория не найдена")
        acc_id.place = body.new_location
        acc_id.date_time = datetime.datetime.now()

        new_acc_event = LogItem(kind_table="Комплектующие",
                                user_id=user["username"],
                                passive_id=body.id,
                                modified_cols=f"комплектующие перемещены",
                                values_of_change=f'{body.new_location}',
                                date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                )

        db.add(acc_id)
        db.add(new_acc_event)
        db.commit()

        # return JSONResponse(content={"data": "комплектующие категории перемещены", "status": True})
        return response(data="комплектующие пермещены", status=True)
