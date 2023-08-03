from typing import Dict

from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from gunicorn.app.base import BaseApplication

import constants
from app.app.controllers import router
from app.app.jobs import job
from config import settings
from core.exceptions import CustomException
from core.utils import logger, scheduler


class Application(BaseApplication):
    def __init__(self, _app: FastAPI, options: Dict[str, str] = None) -> None:
        self.options = options or {}
        self.application = _app
        super().__init__()

    def load_config(self) -> None:
        for key, value in self.options.items():
            self.cfg.set(key.lower(), value)

    def load(self) -> FastAPI:
        return self.application


def init_routers(_app: FastAPI) -> None:
    """
    Initialize all routers.
    """
    _app.include_router(router)
    return


def root_health_path(_app: FastAPI) -> None:
    """
    Health Check Endpoint.
    """

    @_app.get("/", include_in_schema=False)
    def root() -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": constants.SUCCESS})

    @_app.get("/healthcheck", include_in_schema=False)
    def healthcheck() -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": constants.SUCCESS})

    return


def init_middlewares(_app: FastAPI) -> None:
    """
    Middleware initialization.
    """
    _app.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
    )
    return


def start_exception_handlers(_app: FastAPI) -> None:
    """
    Defining Exception Handlers.
    """

    @_app.exception_handler(RequestValidationError)
    async def validation_exception_handler(*args) -> JSONResponse:
        """
        Handler for all the :class:`RequestValidationError` raised within the app.
        """
        exc = args[1]
        logger.exception(f"{exc.__class__.__name__}: {exc.errors()}")
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"error": exc.errors()})

    @_app.exception_handler(CustomException)
    async def custom_exception_handler(*args) -> JSONResponse:
        """
        Handler for all the :class:`CustomException` raised within the app.
        """
        exc = args[1]
        logger.exception(f"{exc.__class__.__name__}: {exc.message}")
        return JSONResponse(status_code=exc.status_code, content={"error": exc.message})

    return


def startup_events(_app: FastAPI) -> None:
    logger.info("Executing all start up functions...")

    @_app.on_event("startup")
    async def starting_scheduler() -> None:
        """
        Startup event.
        """
        logger.info("Starting scheduler")
        scheduler.start()
        scheduler.add_job(job, "cron", hour="23", minute="59", id="check_subscriptions")
        logger.info("Added Subscription check job")
        return None

    return


def shutdown_events(_app: FastAPI) -> None:
    logger.info("Executing all shutdown functions...")

    @_app.on_event("shutdown")
    async def shutdown_scheduler() -> None:
        """
        Shutdown event.
        """
        logger.info("Shutting down scheduler")
        scheduler.shutdown()
        return None

    return


def create_app(debug: bool = False) -> FastAPI:
    """
    Create a Initialize the FastAPI app.
    """
    _app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/docs" if debug else None,
        redoc_url="/redoc" if debug else None,
    )

    init_routers(_app)
    root_health_path(_app)
    init_middlewares(_app)
    start_exception_handlers(_app)
    startup_events(_app)
    shutdown_events(_app)

    return _app


app = create_app()
