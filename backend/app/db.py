"""SQLite-backed persistence helpers for interface 4 event records."""
from __future__ import annotations

import random
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

DB_DIR = Path(__file__).resolve().parents[1] / "data"
DB_PATH = DB_DIR / "interface4_events.sqlite3"


def isoformat(dt: datetime) -> str:
    dt = dt.astimezone(timezone.utc)
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


@contextmanager
def get_connection():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS interface4_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL,
                device_id TEXT,
                point_code TEXT,
                material_code TEXT,
                batch_no TEXT,
                produced_qty REAL,
                unit TEXT,
                trigger_value REAL,
                status TEXT,
                handler TEXT,
                remarks TEXT,
                trigger_source TEXT,
                triggered_at TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_interface4_events_triggered_at ON interface4_events(triggered_at)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_interface4_events_event_id ON interface4_events(event_id)"
        )
        conn.commit()
    seed_events()


def seed_events() -> None:
    """Populate demo data when the table is empty."""
    with get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM interface4_events").fetchone()[0]
        if count:
            return

        base = datetime.utcnow().replace(tzinfo=timezone.utc)
        statuses = ["captured", "processing", "completed", "failed"]
        handlers = ["OPC 触发器", "Modbus 轮询", "产线扫码", "调度回写"]
        materials = [
            ("PA66", "干燥料斗 01"),
            ("ABS-UV", "干燥料斗 03"),
            ("PC+GF", "供料阀站 05"),
            ("TPU", "色母投加 07"),
        ]
        payloads: List[Tuple] = []
        for index in range(32):
            material, device = random.choice(materials)
            qty = round(random.uniform(120, 560), 1)
            triggered_at = isoformat(base - timedelta(minutes=6 * index + random.randint(0, 5)))
            payloads.append(
                (
                    f"EVT-{base:%Y%m%d}{index:03d}",
                    device,
                    f"P{random.randint(100, 999)}",  # point code
                    material,
                    f"B{base:%Y%m%d}{index:03d}",
                    qty,
                    "kg",
                    round(random.uniform(0, 1), 3),
                    random.choice(statuses),
                    random.choice(handlers),
                    "自动采集并入库",
                    random.choice(["OPC_UA", "Modbus"]),
                    triggered_at,
                    triggered_at,
                )
            )

        conn.executemany(
            """
            INSERT INTO interface4_events (
                event_id,
                device_id,
                point_code,
                material_code,
                batch_no,
                produced_qty,
                unit,
                trigger_value,
                status,
                handler,
                remarks,
                trigger_source,
                triggered_at,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            payloads,
        )
        conn.commit()


def ensure_iso(value: str, *, end_of_day: bool = False) -> str:
    value = value.strip()
    if not value:
        raise ValueError("empty timestamp")
    if len(value) == 10:
        dt = datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        if end_of_day:
            dt = dt + timedelta(hours=23, minutes=59, seconds=59)
        return isoformat(dt)
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    dt = datetime.fromisoformat(value)
    if end_of_day and dt.tzinfo:
        dt = dt.astimezone(timezone.utc)
        dt = dt + timedelta(hours=23, minutes=59, seconds=59)
    return isoformat(dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc))


def _apply_filters(
    keyword: Optional[str],
    status: Optional[str],
    start: Optional[str],
    end: Optional[str],
) -> Tuple[str, List[str]]:
    clauses = []
    params: List[str] = []
    if keyword:
        clauses.append("(event_id LIKE ? OR material_code LIKE ? OR device_id LIKE ?)")
        pattern = f"%{keyword}%"
        params.extend([pattern, pattern, pattern])
    if status:
        clauses.append("status = ?")
        params.append(status)
    if start:
        clauses.append("triggered_at >= ?")
        params.append(start)
    if end:
        clauses.append("triggered_at <= ?")
        params.append(end)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    return where, params


def query_interface4_events(
    *,
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Dict[str, object]:
    start_iso = ensure_iso(start) if start else None
    end_iso = ensure_iso(end, end_of_day=True) if end else None
    offset = max(page - 1, 0) * page_size
    where, params = _apply_filters(keyword, status, start_iso, end_iso)
    with get_connection() as conn:
        total = conn.execute(f"SELECT COUNT(*) FROM interface4_events {where}", params).fetchone()[0]
        rows = conn.execute(
            f"""
            SELECT * FROM interface4_events
            {where}
            ORDER BY triggered_at DESC
            LIMIT ? OFFSET ?
            """,
            (*params, page_size, offset),
        ).fetchall()
    return {
        "items": [dict(row) for row in rows],
        "total": total,
        "page": page,
        "pageSize": page_size,
    }


def fetch_interface4_events(
    *,
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> List[Dict[str, object]]:
    start_iso = ensure_iso(start) if start else None
    end_iso = ensure_iso(end, end_of_day=True) if end else None
    where, params = _apply_filters(keyword, status, start_iso, end_iso)
    with get_connection() as conn:
        rows = conn.execute(
            f"""
            SELECT * FROM interface4_events
            {where}
            ORDER BY triggered_at DESC
            """,
            params,
        ).fetchall()
    return [dict(row) for row in rows]


def insert_interface4_event(data: Dict[str, object]) -> Dict[str, object]:
    now = isoformat(datetime.utcnow().replace(tzinfo=timezone.utc))
    event_id = data.get("event_id") or f"EVT-{datetime.utcnow():%Y%m%d%H%M%S}"
    triggered_at = data.get("triggered_at")
    triggered_iso = ensure_iso(triggered_at) if triggered_at else now
    payload = {
        "event_id": event_id,
        "device_id": data.get("device_id"),
        "point_code": data.get("point_code"),
        "material_code": data.get("material_code"),
        "batch_no": data.get("batch_no"),
        "produced_qty": data.get("produced_qty"),
        "unit": data.get("unit") or "kg",
        "trigger_value": data.get("trigger_value"),
        "status": data.get("status") or "captured",
        "handler": data.get("handler") or "接口监听",
        "remarks": data.get("remarks"),
        "trigger_source": data.get("trigger_source") or "OPC_UA",
        "triggered_at": triggered_iso,
        "created_at": now,
    }
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO interface4_events (
                event_id,
                device_id,
                point_code,
                material_code,
                batch_no,
                produced_qty,
                unit,
                trigger_value,
                status,
                handler,
                remarks,
                trigger_source,
                triggered_at,
                created_at
            ) VALUES (:event_id, :device_id, :point_code, :material_code, :batch_no, :produced_qty, :unit, :trigger_value, :status, :handler, :remarks, :trigger_source, :triggered_at, :created_at)
            """,
            payload,
        )
        conn.commit()
        inserted_id = cursor.lastrowid
        row = conn.execute(
            "SELECT * FROM interface4_events WHERE id = ?", (inserted_id,)
        ).fetchone()
    return dict(row)
