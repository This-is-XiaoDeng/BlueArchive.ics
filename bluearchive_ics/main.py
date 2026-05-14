"""FastAPI 主应用"""

from __future__ import annotations

from enum import Enum
from pathlib import Path

from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse

from .calendar import build_calendar
from .scraper import EventType, fetch_all_events, merge_card_pools

app = FastAPI(
    title="BlueArchive.ics",
    description="将蔚蓝档案的卡池和活动信息转换为 iCalendar 日历文件",
    version="0.3.0",
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
    CARD_MERGED = "card/merged"
    FULL_CARD = "full-card-info"
    ASSAULT = "assault"
    EVENT = "event"


# 映射：路径参数 -> (筛选集合, 是否合并卡池)
FILTER_MAP: dict[EventTypeParam, tuple[set[EventType] | None, bool]] = {
    EventTypeParam.BA: (None, True),
    EventTypeParam.ALL: (None, True),
    EventTypeParam.CARD: ({EventType.CARD}, True),
    EventTypeParam.CARD_MERGED: ({EventType.CARD}, True),
    EventTypeParam.FULL_CARD: ({EventType.CARD}, False),
    EventTypeParam.ASSAULT: ({EventType.ASSAULT}, False),
    EventTypeParam.EVENT: ({EventType.EVENT}, False),
}


@app.get("/", response_class=HTMLResponse)
async def index():
    """项目首页"""
    return (TEMPLATE_DIR / "index.html").read_text(encoding="utf-8")


@app.get("/ba.ics")
async def ba_ics_default():
    """默认路由：国服全部事件（兼容旧链接）"""
    return await _generate_ics(ServerType.CN, EventTypeParam.BA)


@app.get("/all.ics")
async def all_ics_default():
    """国服全部事件"""
    return await _generate_ics(ServerType.CN, EventTypeParam.ALL)


@app.get("/card/merged.ics")
async def card_merged_ics_default():
    """国服合并卡池"""
    return await _generate_ics(ServerType.CN, EventTypeParam.CARD_MERGED)


@app.get("/full-card-info.ics")
async def full_card_info_ics_default():
    """国服完整卡池信息（不合并）"""
    return await _generate_ics(ServerType.CN, EventTypeParam.FULL_CARD)


@app.get("/{server}/ba.ics")
async def ba_ics_server(server: ServerType):
    """指定服务器的全部事件"""
    return await _generate_ics(server, EventTypeParam.BA)


@app.get("/{server}/all.ics")
async def all_ics_server(server: ServerType):
    """指定服务器的全部事件"""
    return await _generate_ics(server, EventTypeParam.ALL)


@app.get("/{server}/card/merged.ics")
async def card_merged_ics_server(server: ServerType):
    """指定服务器的合并卡池"""
    return await _generate_ics(server, EventTypeParam.CARD_MERGED)


@app.get("/{server}/full-card-info.ics")
async def full_card_info_ics_server(server: ServerType):
    """指定服务器的完整卡池信息（不合并）"""
    return await _generate_ics(server, EventTypeParam.FULL_CARD)


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
    filters, should_merge = FILTER_MAP[type]

    if should_merge:
        events = merge_card_pools(events)

    ics_content = build_calendar(events, filters=filters)

    filename = f"blue-archive-{server.value}.ics"
    return Response(
        content=ics_content,
        media_type="text/calendar; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
