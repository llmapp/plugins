import os

from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


from src.router import router as plugin_router


load_dotenv()


def add_cors_middleware(app):
    origins = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
        "*"
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@asynccontextmanager
async def lifespan(app: FastAPI):  # collects GPU memory
    yield

api = FastAPI(lifespan=lifespan)

add_cors_middleware(api)


@api.on_event("startup")
async def startup_event():
    print("Starting up...")

prefix = os.environ.get('API_PREFIX', "/api/v1")
api.include_router(plugin_router, prefix=prefix)


@api.on_event("shutdown")
async def shutdown_event():
    print("Shutting down...")


@api.exception_handler(HTTPException)
async def http_exception_handler(_, exception):
    return JSONResponse(status_code=exception.status_code, content={"detail": exception.detail})


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("api:api",
                host=os.environ.get('SERVER_HOST', '0.0.0.0'),
                port=int(os.environ.get('APP_PORT', 8000)),
                reload=True,
                workers=1)
