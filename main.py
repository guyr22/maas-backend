from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse
from database import init_db
from exceptions.collector_not_in_pool_error import CollectorNotInPoolError
from exceptions.job_not_found_error import JobNotFoundError
from exceptions.job_name_exists_error import JobNameExistsError
from exceptions.pool_not_exist_error import PoolNotFoundError
from exceptions.produce_failure_error import ProduceFailureError
from exceptions.unauthorized_api_key import UnauthorizedApiKeyError
from routers.v1 import router
from utils.logger import create_logger

logger = create_logger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    logger.info("Closing application")


app = FastAPI(title="MAAS", lifespan=lifespan)
app.include_router(router)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )

def create_exception_handler(status_code: int):
    async def handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status_code,
            content={"detail": getattr(exc, "message", str(exc))},
        )
    return handler

app.add_exception_handler(CollectorNotInPoolError, create_exception_handler(status.HTTP_400_BAD_REQUEST))
app.add_exception_handler(JobNotFoundError, create_exception_handler(status.HTTP_404_NOT_FOUND))
app.add_exception_handler(JobNameExistsError, create_exception_handler(status.HTTP_409_CONFLICT))
app.add_exception_handler(PoolNotFoundError, create_exception_handler(status.HTTP_404_NOT_FOUND))
app.add_exception_handler(ProduceFailureError, create_exception_handler(status.HTTP_500_INTERNAL_SERVER_ERROR))
app.add_exception_handler(UnauthorizedApiKeyError, create_exception_handler(status.HTTP_401_UNAUTHORIZED))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

