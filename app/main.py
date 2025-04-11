import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.shaders import router as shaders_router
app = FastAPI()
app.include_router(shaders_router)
app.include_router(auth_router)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешенные домены
    allow_credentials=True,
    allow_methods=["*"],  # Разрешенные методы (GET, POST, etc.)
    allow_headers=["*"],  # Разрешенные заголовки
)

if __name__ == '__main__':
    uvicorn.run("app.main:app", host="localhost", port=8000)
