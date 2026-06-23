from fastapi import FastAPI
from app.routers.auth import router as auth_router

app = FastAPI(
    title="Personal Finance API",
    description="Track accounts, transactions, and spending analytics",
    version="1.0.0"
)

app.include_router(auth_router)

@app.get('/health')
def health_check():
    return {'status': 'ok'}