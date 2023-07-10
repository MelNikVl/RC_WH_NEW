import datetime

from fastapi import Depends
from sqlalchemy.orm import Session

from app.crud.materials import MaterialCRUD
from app.utils.auth import user_dependency
from db.db import get_db
from models.models import Material, Repair, Accessories, LogItem


class TestingController:
    @staticmethod
    async def create_10_iterations(user: user_dependency,
                     db: Session = Depends(get_db)):

        for i in range(10):
            new_10_materials = Material(id=i,
                                        user_id=user.get("username"),
                                        category="компьютер",
                                        title=f"pc10{i}",
                                        description="актив для тестирования",
                                        date_time=datetime.datetime.now()
                                        )
            new_10_repair = Repair(material_id=i,
                                   responsible_it_dept_user=user.get("username"),
                                   problem_description="создание карточки актива",
                                   repair_number=1,
                                   date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                   repair_status=False,
                                   repair_unique_id=MaterialCRUD.generate_alphanum_random_string(20)
                                   )
            new_10_accessories = Accessories(category="переходник",
                                      title="vga - hdmi",
                                      count=10,
                                      responsible=user.get("username"),
                                      place="создано для теста. склад 1",
                                      date_time=datetime.datetime.now()
                                      )

            new_test_event = LogItem(kind_table="Тестирование",
                                    user_id=user["username"],
                                    passive_id=555555555555,
                                    modified_cols="разные колонки",
                                    values_of_change="добавлено 10 активов, 10 ремонтов, 10 комплектующих",
                                    date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    )

            db.add(new_10_materials)
            db.add(new_10_repair)
            db.add(new_10_accessories)
            db.add(new_test_event)
            db.commit()

        return "все ок. добавлено"

