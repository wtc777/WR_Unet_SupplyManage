"""FastAPI application exposing a demo API and serving the MVP frontend."""
from __future__ import annotations

from pathlib import Path
from typing import List

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import auth, data, schemas

app = FastAPI(
    title="UNET Supply Management MVP",
    description="Demo API and frontend prototype for the集中供料管理系统",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_current_user(authorization: str = Header(..., alias="Authorization")) -> auth.AuthenticatedUser:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="缺少认证信息")
    prefix = "Bearer "
    if not authorization.startswith(prefix):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="认证格式错误")
    token = authorization[len(prefix) :]
    user = auth.token_store.get_user(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="认证已失效，请重新登录")
    return user


@app.post("/api/auth/login", response_model=schemas.LoginResponse)
def login(credentials: schemas.LoginRequest) -> schemas.LoginResponse:
    user = auth.verify_credentials(credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    token = auth.token_store.issue_token(user)
    return schemas.LoginResponse(
        token=token,
        role=user.role,
        display_name=user.display_name,
        permissions=user.permissions,
    )


@app.get("/api/dashboard/overview", response_model=schemas.DashboardOverview)
def dashboard_overview(_: auth.AuthenticatedUser = Depends(get_current_user)) -> schemas.DashboardOverview:
    return schemas.DashboardOverview(**data.get_dashboard_overview())


@app.get("/api/monitoring/devices", response_model=List[schemas.DeviceStatus])
def monitoring_devices(_: auth.AuthenticatedUser = Depends(get_current_user)) -> List[schemas.DeviceStatus]:
    return [schemas.DeviceStatus(**item) for item in data.list_devices()]


@app.get("/api/tasks", response_model=List[schemas.Task])
def list_tasks(_: auth.AuthenticatedUser = Depends(get_current_user)) -> List[schemas.Task]:
    return [schemas.Task(**item) for item in data.list_tasks()]


@app.post("/api/tasks", response_model=schemas.TaskCreateResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: schemas.TaskCreateRequest, user: auth.AuthenticatedUser = Depends(get_current_user)) -> schemas.TaskCreateResponse:
    task = data.create_task({**payload.dict(), "actor": user.username})
    return schemas.TaskCreateResponse(**task)


@app.get("/api/alerts", response_model=List[schemas.Alert])
def list_alerts(_: auth.AuthenticatedUser = Depends(get_current_user)) -> List[schemas.Alert]:
    return [schemas.Alert(**item) for item in data.list_alerts()]


@app.get("/api/audit/logs", response_model=List[schemas.AuditLog])
def list_audit_logs(_: auth.AuthenticatedUser = Depends(get_current_user)) -> List[schemas.AuditLog]:
    return [schemas.AuditLog(**item) for item in data.list_audit_logs(limit=20)]


@app.get("/api/integrations", response_model=List[schemas.IntegrationStatus])
def list_integrations(_: auth.AuthenticatedUser = Depends(get_current_user)) -> List[schemas.IntegrationStatus]:
    return [schemas.IntegrationStatus(**item) for item in data.get_integrations()]


FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
INDEX_FILE = FRONTEND_DIR / "index.html"

if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR), name="frontend-assets")


@app.get("/", include_in_schema=False)
async def serve_index() -> FileResponse:
    if not INDEX_FILE.exists():
        raise HTTPException(status_code=404, detail="前端尚未构建")
    return FileResponse(INDEX_FILE)
