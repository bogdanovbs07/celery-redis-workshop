from fastapi import FastAPI
from core.database import engine, Base
from routes.jobs import router as jobs_router

# Создаем таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Celery Redis Workshop",
    description="API для работы с фоновыми задачами Celery и Redis",
    version="1.0.0"
)

# Подключаем роутеры
app.include_router(jobs_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to Celery Redis Workshop API",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
