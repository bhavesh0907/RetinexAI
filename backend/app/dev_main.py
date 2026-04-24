# app/dev_main.py

from fastapi import FastAPI # pyright: ignore[reportMissingImports]

app = FastAPI(
    title="RetinexAI Backend (Dev)",
    version="0.1.0"
)

@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "RetinexAI backend is running"
    }
