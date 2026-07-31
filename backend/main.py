"""
CyberShield XDR — FastAPI Application Factory
Creates and configures the FastAPI application with all middleware,
security headers, CORS, rate limiting, and startup/shutdown lifecycle.
"""
import time
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from backend.config.logging_config import get_logger, setup_logging
from backend.config.settings import get_settings
from backend.database.session import close_db, init_db

settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan manager.
    Handles startup (DB init, cache warm-up) and shutdown (connection cleanup).
    """
    # Startup
    setup_logging(
        level="DEBUG" if settings.is_development else "INFO",
        use_json=settings.is_production,
    )
    logger.info(f"Starting {settings.app_name} v{settings.app_version} [{settings.app_env}]")

    if settings.is_development:
        await init_db()

    logger.info("Application startup complete")
    yield

    # Shutdown
    await close_db()
    logger.info("Application shutdown complete")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds security headers to every response.
    Prevents XSS, clickjacking, MIME sniffing, and information leakage.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'"
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        # Remove server identification
        if "server" in response.headers:
            del response.headers["server"]
        return response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attaches a unique request ID to every request for distributed tracing."""
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """
    Global rate limiting backed by Redis.
    Limits standard API requests to RATE_LIMIT_PER_MINUTE.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        # Only rate limit API paths
        if not request.url.path.startswith("/api/v1/"):
            return await call_next(request)
            
        from backend.database.redis_client import RedisKeys, get_redis
        redis = await get_redis()
        ip = request.client.host if request.client else "unknown"
        
        # We skip rate limiting for /auth since it has its own stricter logic
        if request.url.path.startswith("/api/v1/auth/"):
            return await call_next(request)
            
        key = RedisKeys.rate_limit(ip, "global_api")
        count = await redis.incr(key)
        if count == 1:
            await redis.expire(key, 60)
            
        # Hard cap of global limits (e.g., 60 req/min)
        if count > settings.rate_limit_per_minute:
            return JSONResponse(
                status_code=429,
                content={"error": "Too Many Requests", "detail": "Global API rate limit exceeded"},
                headers={"Retry-After": "60"}
            )
            
        return await call_next(request)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Logs all incoming requests with timing for performance monitoring."""
    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            f"{request.method} {request.url.path} → {response.status_code} "
            f"({duration_ms:.1f}ms)",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 1),
                "client_ip": request.client.host if request.client else None,
            },
        )
        return response


def create_app() -> FastAPI:
    """
    Application factory — creates and configures the FastAPI instance.
    Using factory pattern allows easy testing with different configurations.
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AI-Powered Extended Detection and Response Platform",
        docs_url="/api/docs" if not settings.is_production else None,
        redoc_url="/api/redoc" if not settings.is_production else None,
        openapi_url="/api/openapi.json" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # --- Middleware (order matters: outermost runs first on request, last on response) ---
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RateLimitingMiddleware)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
        expose_headers=["X-Request-ID", "X-Total-Count"],
    )

    # --- Exception Handlers ---
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        sanitized = []
        for err in exc.errors():
            clean = {k: v for k, v in err.items() if k not in ("ctx", "input")}
            if "ctx" in err:
                clean["ctx"] = {
                    k: str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v
                    for k, v in err["ctx"].items()
                }
            sanitized.append(clean)
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation Error",
                "detail": sanitized,
                "request_id": getattr(request.state, "request_id", None),
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(
            f"Unhandled exception: {exc}",
            exc_info=True,
            extra={"request_id": getattr(request.state, "request_id", None)},
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "request_id": getattr(request.state, "request_id", None),
            },
        )

    # --- Routers (registered after middleware) ---
    _register_routers(app)

    return app


def _register_routers(app: FastAPI) -> None:
    """Register all API routers with versioned prefix."""
    from backend.api.v1.router import api_router
    app.include_router(api_router, prefix="/api/v1")

    @app.get("/health", tags=["Health"])
    async def health_check():
        """Kubernetes/Docker health check endpoint."""
        return {"status": "healthy", "version": settings.app_version}
