from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.db import init_db
from user.controller import router as user
from userStatistic.controller import router as userStatistic
from userPrivileges.controller import router as userPrivileges
from topics.controller import router as topics

app = FastAPI()
init_db(app)


app.include_router(user, tags=['User'])
app.include_router(userStatistic, tags=['User statistic'])
app.include_router(userPrivileges, tags=['User privileges'])
app.include_router(topics, tags=['Topics'])

# --- Добавление middleware для обработки CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.title = 'CodeRock2024'
