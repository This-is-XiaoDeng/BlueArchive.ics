"""FastAPI 主应用"""

from __future__ import annotations

from enum import Enum
from pathlib import Path

from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse

from .calendar import build_calendar
from .scraper import EventType, fetch_all_events

app = FastAPI(
    title="BlueArchive.ics",
    description="将蔚蓝档案的卡池和活动信息转换为 iCalendar 日历文件",
    version="0.2.0",
)

TEMPLATE_DIR = Path(__file__).parent / "templates"


class ServerType(str, Enum):
    CN = "cn"
    IN = "in"
    JP = "jp"


class EventTypeParam(str, Enum):
    BA = "ba"
    ALL = "all"
    CARD = "card"
    ASSAULT = "assault"
    EVENT = "event"


# 映射：路径参数 -> 筛选集合
FILTER_MAP: dict[EventTypeParam, set[EventType] | None] = {
    EventTypeParam.BA: None,
    EventTypeParam.ALL: None,
    EventTypeParam.CARD: {EventType.CARD},
    EventTypeParam.ASSAULT: {EventType.ASSAULT},
    EventTypeParam.EVENT: {EventType.EVENT},
}


@app.get("/", response_class=HTMLResponse)
async def index():
    """项目首页"""
    return (TEMPLATE_DIR / "index.html").read_text(encoding="utf-8")


@app.get("/ba.ics")
async def ba_ics_default():
    """默认路由：国服全部事件（兼容旧链接）"""
    return await _generate_ics(ServerType.CN, EventTypeParam.BA)


@app.get("/{server}/{type}.ics")
async def ba_ics_server_type(server: ServerType, type: EventTypeParam):
    """指定区服和类型"""
    return await _generate_ics(server, type)


@app.get("/{type}.ics")
async def ba_ics_type(type: EventTypeParam):
    """仅指定类型，默认国服"""
    return await _generate_ics(ServerType.CN, type)


async def _generate_ics(server: ServerType, type: EventTypeParam) -> Response:
    """生成 .ics 文件"""
    events = await fetch_all_events(server.value)
    filters = FILTER_MAP[type]
    ics_content = build_calendar(events, filters=filters)

    filename = f"blue-archive-{server.value}.ics"
    return Response(
        content=ics_content,
        media_type="text/calendar; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
