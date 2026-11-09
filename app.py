from __future__ import annotations

import os
import sqlite3
from contextlib import closing
from datetime import date
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = Path(os.getenv("DATABASE_PATH", DATA_DIR / "transport.db"))

app = FastAPI(title="RN YADAV TRAILER SERVICE", version="0.1.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

STATUSES = ("OPEN", "QUOTING", "ASSIGNED", "IN_TRANSIT", "DELIVERED", "CANCELLED")
AVAILABILITY = ("TO_CONFIRM", "AVAILABLE", "UNAVAILABLE")


def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db() -> None:
    with closing(connect()) as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS loads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reference TEXT NOT NULL UNIQUE,
            caller_name TEXT NOT NULL,
            caller_phone TEXT,
            origin TEXT NOT NULL,
            destination TEXT NOT NULL,
            material TEXT,
            vehicle_type TEXT NOT NULL,
            weight_tonnes REAL,
            offered_rate REAL,
            payment_terms TEXT NOT NULL DEFAULT '',
            notes TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'OPEN',
            enquiry_date TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS transporters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            base_location TEXT NOT NULL DEFAULT '',
            vehicle_types TEXT NOT NULL DEFAULT '',
            notes TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS bids (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            load_id INTEGER NOT NULL REFERENCES loads(id) ON DELETE CASCADE,
            transporter_name TEXT NOT NULL,
            transporter_phone TEXT NOT NULL DEFAULT '',
            vehicle_number TEXT NOT NULL DEFAULT '',
            quoted_rate REAL NOT NULL CHECK (quoted_rate >= 0),
            availability TEXT NOT NULL DEFAULT 'TO_CONFIRM',
            notes TEXT NOT NULL DEFAULT ''
        );
        """)
        db.commit()


@app.on_event("startup")
def startup() -> None:
    init_db()


def optional_number(value: Optional[str], field_name: str) -> Optional[float]:
    if value is None or not value.strip():
        return None
    try:
        parsed = float(value)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=field_name + " must be a number") from exc
    if parsed < 0:
        raise HTTPException(status_code=400, detail=field_name + " cannot be negative")
    return parsed


@app.get("/", name="dashboard")
def dashboard(request: Request, q: str = "", status: str = ""):
    if status and status not in STATUSES:
        raise HTTPException(status_code=400, detail="Invalid status filter")
    with closing(connect()) as db:
        counts = {
            "total": db.execute("SELECT COUNT(*) FROM loads").fetchone()[0],
            "open": db.execute("SELECT COUNT(*) FROM loads WHERE status IN ('OPEN','QUOTING')").fetchone()[0],
            "assigned": db.execute("SELECT COUNT(*) FROM loads WHERE status IN ('ASSIGNED','IN_TRANSIT')").fetchone()[0],
            "delivered": db.execute("SELECT COUNT(*) FROM loads WHERE status='DELIVERED'").fetchone()[0],
        }
        sql = "SELECT * FROM loads WHERE 1=1"
        params: list[str] = []
        if q.strip():
            term = "%" + q.strip() + "%"
            sql += " AND (reference LIKE ? OR caller_name LIKE ? OR origin LIKE ? OR destination LIKE ?)"
            params.extend([term, term, term, term])
        if status:
            sql += " AND status = ?"
            params.append(status)
        sql += " ORDER BY id DESC LIMIT 200"
        loads = db.execute(sql, params).fetchall()
    return templates.TemplateResponse("dashboard.html", {
        "request": request, "counts": counts, "loads": loads, "q": q, "status": status
    })


@app.get("/loads/new")
def new_load(request: Request):
    return templates.TemplateResponse("new_load.html", {"request": request})


@app.post("/loads")
def create_load(
    caller_name: str = Form(...), caller_phone: str = Form(""),
    origin: str = Form(...), destination: str = Form(...),
    material: str = Form(""), vehicle_type: str = Form("Trailer"),
    weight_tonnes: str = Form(""), offered_rate: str = Form(""),
    payment_terms: str = Form(""), notes: str = Form("")
):
    caller_name, origin, destination = caller_name.strip(), origin.strip(), destination.strip()
    if not caller_name or not origin or not destination:
        raise HTTPException(status_code=400, detail="Caller, origin and destination are required")
    weight = optional_number(weight_tonnes, "Weight")
    rate = optional_number(offered_rate, "Offered rate")
    with closing(connect()) as db:
        cursor = db.execute(
            """INSERT INTO loads
            (reference, caller_name, caller_phone, origin, destination, material,
             vehicle_type, weight_tonnes, offered_rate, payment_terms, notes, enquiry_date)
            VALUES ('PENDING', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (caller_name, caller_phone.strip(), origin, destination, material.strip(),
             vehicle_type.strip(), weight, rate, payment_terms.strip(), notes.strip(), date.today().isoformat())
        )
        load_id = cursor.lastrowid
        reference = "RYTS-" + date.today().strftime("%y%m") + "-" + str(load_id).zfill(4)
        db.execute("UPDATE loads SET reference=? WHERE id=?", (reference, load_id))
        db.commit()
    return RedirectResponse(url="/loads/" + str(load_id), status_code=303)


@app.get("/loads/{load_id}")
def load_detail(request: Request, load_id: int):
    with closing(connect()) as db:
        load = db.execute("SELECT * FROM loads WHERE id=?", (load_id,)).fetchone()
        if load is None:
            raise HTTPException(status_code=404, detail="Load not found")
        bids = db.execute("SELECT * FROM bids WHERE load_id=? ORDER BY quoted_rate ASC", (load_id,)).fetchall()
    data = dict(load)
    data["bids"] = bids
    return templates.TemplateResponse("load_detail.html", {"request": request, "load": data})


@app.post("/loads/{load_id}/status")
def update_status(load_id: int, status: str = Form(...)):
    if status not in STATUSES:
        raise HTTPException(status_code=400, detail="Invalid load status")
    with closing(connect()) as db:
        cursor = db.execute("UPDATE loads SET status=? WHERE id=?", (status, load_id))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Load not found")
        db.commit()
    return RedirectResponse(url="/loads/" + str(load_id), status_code=303)


@app.post("/loads/{load_id}/bids")
def add_bid(
    load_id: int, transporter_name: str = Form(...), transporter_phone: str = Form(""),
    vehicle_number: str = Form(""), quoted_rate: str = Form(...),
    availability: str = Form("TO_CONFIRM"), notes: str = Form("")
):
    if availability not in AVAILABILITY:
        raise HTTPException(status_code=400, detail="Invalid availability")
    rate = optional_number(quoted_rate, "Quoted rate")
    if rate is None or not transporter_name.strip():
        raise HTTPException(status_code=400, detail="Transporter name and rate are required")
    with closing(connect()) as db:
        if db.execute("SELECT id FROM loads WHERE id=?", (load_id,)).fetchone() is None:
            raise HTTPException(status_code=404, detail="Load not found")
        db.execute(
            """INSERT INTO bids (load_id, transporter_name, transporter_phone, vehicle_number,
            quoted_rate, availability, notes) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (load_id, transporter_name.strip(), transporter_phone.strip(), vehicle_number.strip(),
             rate, availability, notes.strip())
        )
        db.commit()
    return RedirectResponse(url="/loads/" + str(load_id), status_code=303)


@app.get("/transporters")
def transporter_list(request: Request):
    with closing(connect()) as db:
        transporters = db.execute("SELECT * FROM transporters ORDER BY name COLLATE NOCASE").fetchall()
    return templates.TemplateResponse("transporters.html", {"request": request, "transporters": transporters})


@app.post("/transporters")
def create_transporter(
    name: str = Form(...), phone: str = Form(...),
    base_location: str = Form(""), vehicle_types: str = Form(""), notes: str = Form("")
):
    if not name.strip() or not phone.strip():
        raise HTTPException(status_code=400, detail="Name and phone are required")
    with closing(connect()) as db:
        db.execute(
            "INSERT INTO transporters (name, phone, base_location, vehicle_types, notes) VALUES (?, ?, ?, ?, ?)",
            (name.strip(), phone.strip(), base_location.strip(), vehicle_types.strip(), notes.strip())
        )
        db.commit()
    return RedirectResponse(url="/transporters", status_code=303)


@app.get("/health")
def health():
    return {"status": "ok", "service": "rn-yadav-transport-management"}
