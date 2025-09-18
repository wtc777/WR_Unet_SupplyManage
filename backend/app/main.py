"""FastAPI application exposing a demo API and serving the MVP frontend."""
from __future__ import annotations

import csv
from io import StringIO
from pathlib import Path
from typing import Iterable, List

from fastapi import Depends, FastAPI, Header, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from . import auth, data, db, schemas

app = FastAPI(
    title="UNET Supply Management MVP",
    description="Demo API and frontend prototype for the集中供料管理系统",
    version="0.1.0",
)

db.init_db()

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


@app.get("/api/interface4/events", response_model=schemas.Interface4EventListResponse)
def list_interface4_events(
    keyword: str | None = Query(default=None, description="事件编号、物料或设备模糊匹配"),
    status: str | None = Query(default=None, description="状态过滤"),
    start: str | None = Query(default=None, description="开始时间 (ISO 或日期)"),
    end: str | None = Query(default=None, description="结束时间 (ISO 或日期)"),
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=200, alias="pageSize", description="分页大小"),
    _: auth.AuthenticatedUser = Depends(get_current_user),
) -> schemas.Interface4EventListResponse:
    payload = db.query_interface4_events(
        keyword=keyword,
        status=status,
        start=start,
        end=end,
        page=page,
        page_size=page_size,
    )
    items = [schemas.Interface4Event(**item) for item in payload["items"]]
    return schemas.Interface4EventListResponse(
        items=items,
        total=payload["total"],
        page=payload["page"],
        pageSize=payload["pageSize"],
    )


@app.post(
    "/api/interface4/events",
    response_model=schemas.Interface4Event,
    status_code=status.HTTP_201_CREATED,
)
def create_interface4_event(
    payload: schemas.Interface4EventCreateRequest,
    _: auth.AuthenticatedUser = Depends(get_current_user),
) -> schemas.Interface4Event:
    record = db.insert_interface4_event(payload.dict(exclude_unset=True))
    return schemas.Interface4Event(**record)


@app.get("/api/interface4/events/export", include_in_schema=False)
def export_interface4_events(
    keyword: str | None = Query(default=None, description="事件编号、物料或设备模糊匹配"),
    status: str | None = Query(default=None, description="状态过滤"),
    start: str | None = Query(default=None, description="开始时间 (ISO 或日期)"),
    end: str | None = Query(default=None, description="结束时间 (ISO 或日期)"),
    _: auth.AuthenticatedUser = Depends(get_current_user),
) -> StreamingResponse:
    events = db.fetch_interface4_events(
        keyword=keyword,
        status=status,
        start=start,
        end=end,
    )

    headers = [
        "事件编号",
        "触发时间",
        "设备/料斗",
        "点位",
        "物料",
        "批次",
        "产出数量",
        "单位",
        "触发值",
        "状态",
        "来源",
        "处理通道",
        "备注",
    ]

    def generate() -> Iterable[str]:
        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow(headers)
        yield buffer.getvalue()
        buffer.seek(0)
        buffer.truncate(0)
        for item in events:
            writer.writerow(
                [
                    item.get("event_id"),
                    item.get("triggered_at"),
                    item.get("device_id"),
                    item.get("point_code"),
                    item.get("material_code"),
                    item.get("batch_no"),
                    item.get("produced_qty"),
                    item.get("unit"),
                    item.get("trigger_value"),
                    item.get("status"),
                    item.get("trigger_source"),
                    item.get("handler"),
                    item.get("remarks"),
                ]
            )
            yield buffer.getvalue()
            buffer.seek(0)
            buffer.truncate(0)

    response = StreamingResponse(generate(), media_type="text/csv; charset=utf-8")
    response.headers["Content-Disposition"] = "attachment; filename=interface4_events.csv"
    return response


FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
INDEX_FILE = FRONTEND_DIR / "index.html"

if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR), name="frontend-assets")


@app.get("/", include_in_schema=False)
async def serve_index() -> FileResponse:
    if not INDEX_FILE.exists():
        raise HTTPException(status_code=404, detail="前端尚未构建")
    return FileResponse(INDEX_FILE)
