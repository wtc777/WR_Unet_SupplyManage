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
