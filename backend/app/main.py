from fastapi import FastAPI

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