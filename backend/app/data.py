"""Demo data providers for the UNET Supply Management MVP."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta
import itertools
import random
from typing import Dict, List, Optional

ISO_FORMAT = "%Y-%m-%dT%H:%M:%S"


def _ts() -> str:
    return datetime.utcnow().strftime(f"{ISO_FORMAT}Z")


USERS: Dict[str, Dict[str, object]] = {
    "admin": {
        "password": "admin123",
        "display_name": "张主管",
        "role": "系统管理员",
        "permissions": [
            "dashboard.view",
            "tasks.manage",
            "alerts.manage",
            "users.view",
        ],
    },
    "operator": {
        "password": "op2024",
        "display_name": "李操作",
        "role": "现场操作员",
        "permissions": [
            "dashboard.view",
            "tasks.execute",
            "alerts.view",
        ],
    },
    "viewer": {
        "password": "guest",
        "display_name": "访客",
        "role": "只读用户",
        "permissions": [
            "dashboard.view",
            "alerts.view",
        ],
    },
}


DASHBOARD_STATE: Dict[str, object] = {
    "activeTasks": 6,
    "completedToday": 42,
    "equipmentOnline": 8,
    "alarmCount": 2,
    "throughput": 1280.0,
    "energyUsage": 780.0,
    "lastUpdated": _ts(),
}

MATERIAL_SUMMARY: List[Dict[str, object]] = [
    {
        "materialCode": "PA66",
        "hopper": "Hopper01",
        "throughput": 420.0,
        "trend": 6.5,
    },
    {
        "materialCode": "ABS-UV",
        "hopper": "Hopper03",
        "throughput": 315.0,
        "trend": -3.1,
    },
    {
        "materialCode": "PC+GF",
        "hopper": "Hopper05",
        "throughput": 290.0,
        "trend": 2.8,
    },
    {
        "materialCode": "TPU",
        "hopper": "Hopper07",
        "throughput": 255.0,
        "trend": 1.4,
    },
]

DEVICES: List[Dict[str, object]] = [
    {
        "deviceId": "Hopper01",
        "name": "干燥料斗 01",
        "status": "online",
        "material": "PA66",
        "temperature": 82.5,
        "level": 68,
        "lastHeartbeat": _ts(),
        "throughput": 58.2,
        "alarms": [],
    },
    {
        "deviceId": "Hopper02",
        "name": "干燥料斗 02",
        "status": "online",
        "material": "PA66",
        "temperature": 79.4,
        "level": 55,
        "lastHeartbeat": _ts(),
        "throughput": 52.7,
        "alarms": [],
    },
    {
        "deviceId": "Hopper03",
        "name": "混料料斗 03",
        "status": "online",
        "material": "ABS-UV",
        "temperature": 70.1,
        "level": 62,
        "lastHeartbeat": _ts(),
        "throughput": 49.3,
        "alarms": ["温度偏高"],
    },
    {
        "deviceId": "Hopper04",
        "name": "计量料斗 04",
        "status": "maintenance",
        "material": "ABS-UV",
        "temperature": 64.2,
        "level": 45,
        "lastHeartbeat": _ts(),
        "throughput": 0.0,
        "alarms": ["维护中"],
    },
    {
        "deviceId": "Hopper05",
        "name": "供料阀站 05",
        "status": "online",
        "material": "PC+GF",
        "temperature": 66.8,
        "level": 74,
        "lastHeartbeat": _ts(),
        "throughput": 63.5,
        "alarms": [],
    },
    {
        "deviceId": "Hopper06",
        "name": "供料阀站 06",
        "status": "online",
        "material": "PC+GF",
        "temperature": 68.9,
        "level": 71,
        "lastHeartbeat": _ts(),
        "throughput": 60.4,
        "alarms": [],
    },
    {
        "deviceId": "Hopper07",
        "name": "色母投加 07",
        "status": "online",
        "material": "TPU",
        "temperature": 64.0,
        "level": 58,
        "lastHeartbeat": _ts(),
        "throughput": 41.2,
        "alarms": [],
    },
    {
        "deviceId": "Dryer01",
        "name": "中央干燥机",
        "status": "online",
        "material": "集中供料",
        "temperature": 95.3,
        "level": 88,
        "lastHeartbeat": _ts(),
        "throughput": 92.6,
        "alarms": ["滤网差压偏高"],
    },
    {
        "deviceId": "Vacuum01",
        "name": "真空泵组",
        "status": "online",
        "material": "集中供料",
        "temperature": 58.2,
        "level": 100,
        "lastHeartbeat": _ts(),
        "throughput": 110.1,
        "alarms": [],
    },
]

TASKS: List[Dict[str, object]] = [
    {
        "taskId": "T20231018001",
        "materialCode": "PA66",
        "targetDevice": "Hopper01",
        "quantity": 520,
        "priority": "high",
        "status": "in_progress",
        "progress": 68,
        "scheduledAt": "2023-10-18T08:15:00Z",
        "updatedAt": _ts(),
        "source": "ERP",
    },
    {
        "taskId": "T20231018002",
        "materialCode": "ABS-UV",
        "targetDevice": "Hopper03",
        "quantity": 430,
        "priority": "medium",
        "status": "queued",
        "progress": 0,
        "scheduledAt": "2023-10-18T09:00:00Z",
        "updatedAt": _ts(),
        "source": "MES",
    },
    {
        "taskId": "T20231018003",
        "materialCode": "PC+GF",
        "targetDevice": "Hopper05",
        "quantity": 610,
        "priority": "high",
        "status": "in_progress",
        "progress": 42,
        "scheduledAt": "2023-10-18T09:30:00Z",
        "updatedAt": _ts(),
        "source": "ERP",
    },
    {
        "taskId": "T20231018004",
        "materialCode": "TPU",
        "targetDevice": "Hopper07",
        "quantity": 360,
        "priority": "low",
        "status": "completed",
        "progress": 100,
        "scheduledAt": "2023-10-18T07:45:00Z",
        "updatedAt": "2023-10-18T08:40:00Z",
        "source": "Local",
    },
    {
        "taskId": "T20231018005",
        "materialCode": "PA66",
        "targetDevice": "Vacuum01",
        "quantity": 720,
        "priority": "high",
        "status": "in_progress",
        "progress": 25,
        "scheduledAt": "2023-10-18T10:00:00Z",
        "updatedAt": _ts(),
        "source": "ERP",
    },
]

ALERTS: List[Dict[str, object]] = [
    {
        "alertId": "A2023101801",
        "deviceId": "Dryer01",
        "severity": "critical",
        "message": "中央干燥机滤网差压高于阈值",
        "raisedAt": "2023-10-18T07:55:00Z",
        "acknowledged": False,
    },
    {
        "alertId": "A2023101802",
        "deviceId": "Hopper03",
        "severity": "warning",
        "message": "混料料斗温度接近上限",
        "raisedAt": "2023-10-18T08:25:00Z",
        "acknowledged": False,
    },
    {
        "alertId": "A2023101803",
        "deviceId": "Vacuum01",
        "severity": "info",
        "message": "真空泵组按计划完成点检",
        "raisedAt": "2023-10-18T06:40:00Z",
        "acknowledged": True,
    },
]

AUDIT_LOGS: List[Dict[str, object]] = [
    {
        "logId": "L20231018001",
        "category": "任务调度",
        "description": "管理员张主管通过 ERP 接口下发任务 T20231018001",
        "actor": "admin",
        "timestamp": "2023-10-18T07:55:00Z",
    },
    {
        "logId": "L20231018002",
        "category": "报警",
        "description": "中央干燥机触发差压高报警",
        "actor": "system",
        "timestamp": "2023-10-18T07:56:30Z",
    },
    {
        "logId": "L20231018003",
        "category": "任务调度",
        "description": "操作员李操作确认任务 T20231018003 开始执行",
        "actor": "operator",
        "timestamp": "2023-10-18T08:05:00Z",
    },
    {
        "logId": "L20231018004",
        "category": "系统",
        "description": "Modbus 采集周期调整为 5 秒",
        "actor": "admin",
        "timestamp": "2023-10-18T08:20:00Z",
    },
]

INTEGRATIONS: List[Dict[str, object]] = [
    {
        "name": "Modbus 采集",
        "target": "9 台集中供料设备",
        "status": "online",
        "latencyMs": 42,
        "lastUpdated": _ts(),
    },
    {
        "name": "OPC UA 服务",
        "target": "InPlant SCADA",
        "status": "online",
        "latencyMs": 85,
        "lastUpdated": _ts(),
    },
    {
        "name": "ERP 任务接口",
        "target": "第三方 ERP",
        "status": "degraded",
        "latencyMs": 210,
        "lastUpdated": _ts(),
    },
]

_task_sequence = itertools.count(start=6)
_last_simulation = datetime.utcnow()


STATUS_TRANSITIONS = {
    "queued": ["in_progress"],
    "in_progress": ["in_progress", "completed"],
}


def _simulate_devices() -> None:
    for device in DEVICES:
        device["temperature"] = round(device["temperature"] + random.uniform(-0.8, 0.9), 1)
        device["temperature"] = max(30.0, min(120.0, device["temperature"]))
        device["level"] = max(0, min(100, device["level"] + random.randint(-4, 4)))
        if device["status"] != "offline" and random.random() < 0.05:
            device["status"] = random.choice(["online", "maintenance"])
        if device["status"] == "maintenance" and random.random() < 0.3:
            device["status"] = "online"
        if device["status"] == "online":
            device["throughput"] = round(max(0.0, device["throughput"] + random.uniform(-4, 5)), 1)
        device["lastHeartbeat"] = _ts()


def _simulate_tasks() -> None:
    for task in TASKS:
        if task["status"] == "queued" and random.random() < 0.3:
            task["status"] = "in_progress"
            task["updatedAt"] = _ts()
        if task["status"] == "in_progress":
            task["progress"] = min(100, task["progress"] + random.randint(3, 12))
            task["updatedAt"] = _ts()
            if task["progress"] >= 100:
                task["status"] = "completed"
                task["progress"] = 100
                task["updatedAt"] = _ts()
                AUDIT_LOGS.insert(
                    0,
                    {
                        "logId": f"L{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                        "category": "任务调度",
                        "description": f"任务 {task['taskId']} 已自动标记完成",
                        "actor": "system",
                        "timestamp": _ts(),
                    },
                )
    while len(AUDIT_LOGS) > 50:
        AUDIT_LOGS.pop()


def _simulate_alerts() -> None:
    if random.random() < 0.1:
        alert = random.choice(ALERTS)
        if not alert["acknowledged"] and random.random() < 0.4:
            alert["acknowledged"] = True
    if random.random() < 0.12:
        severity = random.choice(["warning", "critical", "info"])
        device = random.choice(DEVICES)
        alert = {
            "alertId": f"A{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "deviceId": device["deviceId"],
            "severity": severity,
            "message": f"{device['name']} 触发{severity}级提醒",
            "raisedAt": _ts(),
            "acknowledged": False,
        }
        ALERTS.insert(0, alert)
    while len(ALERTS) > 20:
        ALERTS.pop()


def _simulate_integrations() -> None:
    for integration in INTEGRATIONS:
        jitter = random.randint(-8, 9)
        integration["latencyMs"] = max(15, integration["latencyMs"] + jitter)
        if integration["name"].startswith("ERP") and integration["latencyMs"] > 250:
            integration["status"] = "degraded"
        elif integration["latencyMs"] > 180:
            integration["status"] = "degraded"
        else:
            integration["status"] = "online"
        if random.random() < 0.05:
            integration["status"] = "offline"
        elif integration["status"] == "offline" and random.random() < 0.5:
            integration["status"] = "online"
        integration["lastUpdated"] = _ts()


def _simulate_materials() -> None:
    for item in MATERIAL_SUMMARY:
        item["throughput"] = round(max(150.0, item["throughput"] + random.uniform(-20, 22)), 1)
        item["trend"] = round(random.uniform(-8, 9), 1)


def simulate_tick() -> None:
    global _last_simulation
    now = datetime.utcnow()
    if now - _last_simulation < timedelta(seconds=3):
        return
    _last_simulation = now
    _simulate_devices()
    _simulate_tasks()
    _simulate_alerts()
    _simulate_integrations()
    _simulate_materials()
    DASHBOARD_STATE["activeTasks"] = sum(1 for task in TASKS if task["status"] in {"queued", "in_progress"})
    DASHBOARD_STATE["completedToday"] = sum(1 for task in TASKS if task["status"] == "completed")
    DASHBOARD_STATE["equipmentOnline"] = sum(1 for device in DEVICES if device["status"] == "online")
    DASHBOARD_STATE["alarmCount"] = sum(1 for alert in ALERTS if not alert["acknowledged"])
    DASHBOARD_STATE["throughput"] = round(
        sum(device["throughput"] for device in DEVICES if device["status"] == "online"), 1
    )
    DASHBOARD_STATE["energyUsage"] = round(720 + random.uniform(-35, 40), 1)
    DASHBOARD_STATE["lastUpdated"] = _ts()


def get_dashboard_overview() -> Dict[str, object]:
    simulate_tick()
    result = deepcopy(DASHBOARD_STATE)
    result["materialSummary"] = deepcopy(MATERIAL_SUMMARY)
    return result


def list_devices() -> List[Dict[str, object]]:
    simulate_tick()
    return deepcopy(DEVICES)


def list_tasks() -> List[Dict[str, object]]:
    simulate_tick()
    return deepcopy(TASKS)


def create_task(payload: Dict[str, object]) -> Dict[str, object]:
    task_id = f"T{datetime.utcnow().strftime('%Y%m%d')}{next(_task_sequence):03d}"
    now = _ts()
    task = {
        "taskId": task_id,
        "materialCode": payload.get("materialCode", ""),
        "targetDevice": payload.get("targetDevice", ""),
        "quantity": int(payload.get("quantity", 0)),
        "priority": payload.get("priority", "medium"),
        "status": "queued",
        "progress": 0,
        "scheduledAt": payload.get("scheduledAt", now),
        "updatedAt": now,
        "source": payload.get("source", "Manual"),
    }
    TASKS.insert(0, task)
    AUDIT_LOGS.insert(
        0,
        {
            "logId": f"L{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "category": "任务调度",
            "description": f"创建手动任务 {task_id}，目标 {task['targetDevice']}",
            "actor": payload.get("actor", "admin"),
            "timestamp": now,
        },
    )
    while len(TASKS) > 30:
        TASKS.pop()
    while len(AUDIT_LOGS) > 50:
        AUDIT_LOGS.pop()
    DASHBOARD_STATE["activeTasks"] = sum(1 for task in TASKS if task["status"] in {"queued", "in_progress"})
    DASHBOARD_STATE["lastUpdated"] = now
    return deepcopy(task)


def list_alerts() -> List[Dict[str, object]]:
    simulate_tick()
    return deepcopy(ALERTS)


def list_audit_logs(limit: Optional[int] = None) -> List[Dict[str, object]]:
    simulate_tick()
    logs = deepcopy(AUDIT_LOGS)
    if limit is not None:
        return logs[:limit]
    return logs


def get_integrations() -> List[Dict[str, object]]:
    simulate_tick()
    return deepcopy(INTEGRATIONS)
