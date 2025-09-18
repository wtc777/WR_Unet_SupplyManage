"""Pydantic models shared by the FastAPI routes."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class Schema(BaseModel):
    class Config:
        allow_population_by_field_name = True
        orm_mode = True


class LoginRequest(Schema):
    username: str = Field(..., description="用户登录名")
    password: str = Field(..., description="登录密码")


class LoginResponse(Schema):
    token: str
    role: str
    displayName: str = Field(..., alias="display_name")
    permissions: List[str]


class MaterialSummary(Schema):
    materialCode: str
    hopper: str
    throughput: float
    trend: float


class DashboardOverview(Schema):
    activeTasks: int
    completedToday: int
    equipmentOnline: int
    alarmCount: int
    throughput: float
    energyUsage: float
    lastUpdated: str
    materialSummary: List[MaterialSummary]


class DeviceStatus(Schema):
    deviceId: str
    name: str
    status: str
    material: str
    temperature: float
    level: int
    lastHeartbeat: str
    throughput: float
    alarms: List[str]


class Task(Schema):
    taskId: str
    materialCode: str
    targetDevice: str
    quantity: int
    priority: str
    status: str
    progress: int
    scheduledAt: str
    updatedAt: str
    source: str


class TaskCreateRequest(Schema):
    materialCode: str
    targetDevice: str
    quantity: int
    priority: str = Field(default="medium")
    scheduledAt: Optional[str] = None
    source: Optional[str] = "Manual"


class TaskCreateResponse(Task):
    pass


class Alert(Schema):
    alertId: str
    deviceId: str
    severity: str
    message: str
    raisedAt: str
    acknowledged: bool


class AuditLog(Schema):
    logId: str
    category: str
    description: str
    actor: str
    timestamp: str


class IntegrationStatus(Schema):
    name: str
    target: str
    status: str
    latencyMs: int
    lastUpdated: str


class Interface4Event(Schema):
    id: int
    eventId: str = Field(..., alias="event_id")
    deviceId: Optional[str] = Field(None, alias="device_id")
    pointCode: Optional[str] = Field(None, alias="point_code")
    materialCode: Optional[str] = Field(None, alias="material_code")
    batchNo: Optional[str] = Field(None, alias="batch_no")
    producedQty: Optional[float] = Field(None, alias="produced_qty")
    unit: Optional[str]
    triggerValue: Optional[float] = Field(None, alias="trigger_value")
    status: Optional[str]
    handler: Optional[str]
    remarks: Optional[str]
    triggerSource: Optional[str] = Field(None, alias="trigger_source")
    triggeredAt: str = Field(..., alias="triggered_at")
    createdAt: str = Field(..., alias="created_at")


class Interface4EventCreateRequest(Schema):
    eventId: Optional[str] = Field(None, alias="event_id")
    deviceId: Optional[str] = Field(None, alias="device_id")
    pointCode: Optional[str] = Field(None, alias="point_code")
    materialCode: Optional[str] = Field(None, alias="material_code")
    batchNo: Optional[str] = Field(None, alias="batch_no")
    producedQty: Optional[float] = Field(None, alias="produced_qty")
    unit: Optional[str] = None
    triggerValue: Optional[float] = Field(None, alias="trigger_value")
    status: Optional[str] = None
    handler: Optional[str] = None
    remarks: Optional[str] = None
    triggerSource: Optional[str] = Field(None, alias="trigger_source")
    triggeredAt: Optional[str] = Field(None, alias="triggered_at")


class Interface4EventListResponse(Schema):
    items: List[Interface4Event]
    total: int
    page: int
    pageSize: int
