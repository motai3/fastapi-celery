import uuid
from typing import Any

from celery.result import AsyncResult
from fastapi import APIRouter, Body, FastAPI, Form, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/")
def read_items(request: Request) -> Any:
    """
    暂时返回主页面
    """

    return templates.TemplateResponse("home.html", context={"request": request})
