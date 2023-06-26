from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.routes import router, materials, geolocation, auth, logs
from db.db import engine
from models.models import Base
from fastapi.staticfiles import StaticFiles

# создание бд если ее нет (да - втоторой раз) но это ни на что не влияет
Base.metadata.create_all(bind=engine)

# метод для работы с фастапи
app = FastAPI(
    title="RC WH MO tracker",  # Set the new project name
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

app.mount("/static", StaticFiles(directory="static"), name="static")