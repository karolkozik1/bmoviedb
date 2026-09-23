from fastapi import FastAPI
from sqlalchemy import text

from app.db.session import engine

app = FastAPI(
    title="BmovieDb API",
    description="Backend API for BmovieDb",
    version="0.1.0",
)

@app.get("/")
async def root():
    return {"message": "BMovieDb API is running"
    }
    
@app.get("/health")
async def health():
    return {"status": "ok"
    }  
    
@app.get("/health/database")
async def health_database():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1")).scalar_one()
        if result == 1:
            return {"status": "ok", "result": result}
        return {"status": "error", "message": "Database connection failed"}