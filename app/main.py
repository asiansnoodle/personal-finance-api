from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from app.exceptions import FinanceAPIException
from app.routers.auth import router as auth_router
from app.routers.accounts import router as accounts_router
from app.routers.transactions import router as transactions_router
from app.routers.analytics import router as analytics_router
from app.routers.budgets import router as budgets_router

app = FastAPI(
    title="Personal Finance API",
    description="Track accounts, transactions, and spending analytics",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(accounts_router)
app.include_router(transactions_router)
app.include_router(analytics_router)
app.include_router(budgets_router)

@app.get('/health')
def health_check():
    return {'status': 'ok'}

@app.exception_handler(FinanceAPIException)
async def finance_exception_handler(request: Request, exc: FinanceAPIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error,
            "detail": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "detail": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred",
            "status_code": 500
        }
    )
