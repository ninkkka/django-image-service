from fastapi import Request
from fastapi.responses import JSONResponse
from .exceptions import AppException

async def app_exception_handler(request: Request, exc: AppException):
    """Глобальный обработчик исключений"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code
        },
        headers=exc.headers
    )

async def generic_exception_handler(request: Request, exc: Exception):
    """Обработчик для всех остальных исключений"""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Внутренняя ошибка сервера",
            "status_code": 500
        }
    )