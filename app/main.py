import logging
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette import status
from contextlib import asynccontextmanager

from app.logging_config import configure_logging
from app.routes import auth_router, api_router


configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    logger.info("Application shutdown complete")


app = FastAPI(title="Web Scraper API", lifespan=lifespan)

app.include_router(auth_router, prefix="/auth")
app.include_router(api_router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s -> %s (%.1f ms)",
        request.method,
        request.url.path,
        response.status_code,
        ms,
    )
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        {"detail": "Internal server error"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
