from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from prometheus_client import make_asgi_app, Counter, Histogram
import time

from .api.routes import router
from .core.config import settings
from .core.exception_handlers import app_exception_handler, generic_exception_handler
from .core.exceptions import AppException
from .services.django_service import DjangoService
from .services.ocr_service import OCRService
from .services.email_service import EmailService

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan менеджер для управления состоянием приложения
    """
    logger.info("🚀 Starting up FastAPI OCR Service...")
    
    app.state.django_service = DjangoService()
    app.state.ocr_service = OCRService()
    app.state.email_service = EmailService()
    
    try:
        from .tasks.celery_app import celery_app
        celery_app.control.ping()
        logger.info("✅ Celery connected successfully")
    except Exception as e:
        logger.warning(f"⚠️ Celery connection warning: {str(e)}")
    
    logger.info("✅ FastAPI OCR Service started successfully")
    
    yield
    
    logger.info("🛑 Shutting down FastAPI OCR Service...")
    logger.info("👋 FastAPI OCR Service stopped")

def create_app() -> FastAPI:
    """
    Фабрика приложения FastAPI
    """
    app = FastAPI(
        title="Image OCR Service",
        description="Микросервис для распознавания текста на изображениях",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/api/docs" if settings.DEBUG else None,
        redoc_url="/api/redoc" if settings.DEBUG else None,
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.middleware("http")
    async def metrics_middleware(request, call_next):
        """Middleware для сбора метрик"""
        method = request.method
        path = request.url.path
        
        request_count.labels(method=method, endpoint=path).inc()
        
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        
        request_duration.labels(method=method, endpoint=path).observe(duration)
        
        return response
    
    app.include_router(router)
    
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
    
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    
    @app.get("/health", tags=["Health"])
    async def health_check():
        return {
            "status": "healthy",
            "service": "FastAPI OCR Service",
            "version": "1.0.0"
        }
    
    @app.get("/", tags=["Root"])
    async def root():
        return {
            "message": "Image OCR Service API",
            "docs": "/api/docs" if settings.DEBUG else None,
            "version": "1.0.0"
        }
    
    logger.info("✅ FastAPI app created successfully")
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.DEBUG,
        log_level="info"
    )