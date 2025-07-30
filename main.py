from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import sqlite3
import csv
import io

# Time zone support
try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except ImportError:
    from pytz import timezone as ZoneInfo  # Fallback for Python < 3.9

app = FastAPI()
templates = Jinja2Templates(directory="templates")
DB_FILE = "maintenance_logs.db"
TIMEZONE = ZoneInfo("America/New_York")

class LogEntry(BaseModel):
    timestamp: str
    user: str
    action: str
    system: str

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            user TEXT,
            action TEXT,
            system TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.post("/log")
async def receive_log(entry: LogEntry):
    try:
        # Convert to EST (standardized storage)
        try:
            dt = datetime.fromisoformat(entry.timestamp.replace("Z", "+00:00"))  # handle Zulu
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid timestamp format")

        dt_est = dt.astimezone(TIMEZONE)
        formatted = dt_est.isoformat()

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO logs (timestamp, user, action, system) VALUES (?, ?, ?, ?)",
                  (formatted, entry.user, entry.action, entry.system))
        conn.commit()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_logs(user=None, system=None, start_time=None, end_time=None, action=None):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    filters = []
    params = []

    if user:
        filters.append("user = ?")
        params.append(user)
    if system:
        filters.append("system = ?")
        params.append(system)
    if action:
        filters.append("action LIKE ?")
        params.append(f"%{action}%")
    if start_time:
        filters.append("timestamp >= ?")
        params.append(start_time)
    if end_time:
        filters.append("timestamp <= ?")
        params.append(end_time)

    where_clause = " WHERE " + " AND ".join(filters) if filters else ""
    query = f"SELECT timestamp, user, system, action FROM logs{where_clause} ORDER BY timestamp DESC"

    c.execute(query, tuple(params))
    rows = c.fetchall()
    conn.close()
    return rows

@app.get("/log", response_class=HTMLResponse)
async def view_logs(request: Request,
                    user: Optional[str] = None,
                    system: Optional[str] = None,
                    action: Optional[str] = None,
                    start_time: Optional[str] = None,
                    end_time: Optional[str] = None):
    logs = get_logs(user, system, start_time, end_time, action)
    return templates.TemplateResponse("logs.html", {
        "request": request,
        "logs": logs,
        "filters": {
            "user": user or "",
            "system": system or "",
            "action": action or "",
            "start_time": start_time or "",
            "end_time": end_time or ""
        }
    })

@app.get("/export/csv")
async def export_csv(
    user: Optional[str] = None,
    system: Optional[str] = None,
    action: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    range: Optional[str] = None
):
    try:
        if range == "30days":
            # Use the same timestamp format as stored in DB
            now = datetime.now(TIMEZONE)
            start_time = (now - timedelta(days=30)).isoformat()
            end_time = now.isoformat()

        logs = get_logs(user, system, start_time, end_time, action)

        if not logs:
            # Create dummy row so user sees column headers
            logs = []

        output = io.StringIO(newline="")
        writer = csv.writer(output)
        writer.writerow(["Timestamp", "User", "System", "Action"])
        for log in logs:
            writer.writerow(log)

        output.seek(0)
        return StreamingResponse(output, media_type="text/csv", headers={
            "Content-Disposition": "attachment; filename=logs_export.csv"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {e}")