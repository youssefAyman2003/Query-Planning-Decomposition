from __future__ import annotations

import os
import threading
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault("USER_AGENT", "query-planning-decomposition/0.1")

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from src.schemas import QueryRequest, QueryResponse, StatusResponse

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

_pipeline = None
_init_error: str | None = None
_lock = threading.Lock()


def get_pipeline():
    global _pipeline, _init_error
    if _pipeline is not None:
        return _pipeline
    with _lock:
        if _pipeline is not None:
            return _pipeline
        try:
            from src.pipeline import QueryPlanningPipeline

            _pipeline = QueryPlanningPipeline()
            _init_error = None
        except Exception as exc:
            _init_error = str(exc)
            raise
        return _pipeline


def _warmup() -> None:
    try:
        get_pipeline()
    except Exception:
        pass


@asynccontextmanager
async def lifespan(_app: FastAPI):
    thread = threading.Thread(target=_warmup, daemon=True)
    thread.start()
    yield


app = FastAPI(
    title="Query Planning Decomposition",
    description="Break a complex question into sub-queries, retrieve evidence, and answer.",
    version="0.1.0",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/api/status", response_model=StatusResponse)
def status() -> StatusResponse:
    return StatusResponse(ready=_pipeline is not None, error=_init_error)


@app.post("/api/query", response_model=QueryResponse)
def query(payload: QueryRequest) -> QueryResponse:
    if _init_error and _pipeline is None:
        raise HTTPException(status_code=503, detail=_init_error)
    try:
        pipeline = get_pipeline()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return pipeline.invoke_response(payload.question.strip())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
