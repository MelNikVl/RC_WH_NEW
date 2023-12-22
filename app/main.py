from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.routes import router, materials, geolocation, auth, logs, accessories, testing, for_admins
from db.db import engine
from models.models import Base
from fastapi.staticfiles import StaticFiles
try:
    from app.autoupdate import Updater
except ImportError:
    pass

# создание бд если ее нет (да - втоторой раз) но это ни на что не влияет
Base.metadata.create_all(bind=engine)

# метод для работы с фастапи
app = FastAPI(
    title="RC WH MO tracker.",  # Set the new project name
    version="3.1",  # Set the project version
    description="здесь все методы работы с API"  # Set the project description
)

# ебота из документации - типа разрешено обращаться с разных адресов
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# добавление роутеров (эта тема что бы связывать урлы с функциями)
# добавление папки статик для отображения фронта
app.include_router(router)
app.include_router(materials)
app.include_router(geolocation)
app.include_router(auth)
app.include_router(logs)
app.include_router(accessories)
app.include_router(testing)
app.include_router(for_admins)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/it_warehouse_docs", StaticFiles(directory="it_warehouse_docs"), name="it_warehouse_docs")

try:
    Updater()
except Exception as e:
    print(e)
    pass
