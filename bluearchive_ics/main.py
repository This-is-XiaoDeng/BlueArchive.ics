"""FastAPI 主应用"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Query, Response
from fastapi.responses import HTMLResponse

from .calendar import build_calendar
from .scraper import EventType, fetch_all_events

app = FastAPI(
    title="BlueArchive.ics",
    description="将蔚蓝档案的卡池和活动信息转换为 iCalendar 日历文件",
    version="0.1.0",
)

TEMPLATE_DIR = Path(__file__).parent / "templates"


class ServerType(str, Enum):
    CN = "cn"
    IN = "in"
    JP = "jp"


@app.get("/", response_class=HTMLResponse)
async def index():
    """项目首页"""
    return (TEMPLATE_DIR / "index.html").read_text(encoding="utf-8")


@app.get("/ba.ics")
async def ba_ics(
    server: ServerType = ServerType.CN,
    filter: Annotated[list[EventType] | None, Query()] = None,
):
    """返回蔚蓝档案活动日历 .ics 文件

    Args:
        server: 区服 (cn/in/jp)
        filter: 事件类型筛选，可重复 (assault/event/card)
    """
    events = await fetch_all_events(server.value)

    filters = set(filter) if filter else None
    ics_content = build_calendar(events, filters=filters)

    filename = f"blue-archive-{server.value}.ics"
    return Response(
        content=ics_content,
        media_type="text/calendar; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
