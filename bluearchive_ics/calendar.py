"""iCalendar 日历生成模块"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

from icalendar import Calendar, Event

from .scraper import EventType, GameEvent

PRODID = "-//BlueArchive.ics//CN"
CAL_NAME = "蔚蓝档案活动日历"


def _make_uid(event: GameEvent) -> str:
    """生成唯一事件 ID"""
    return f"ba-{event.event_type.value}-{event.id}@bluearchive-ics"


def _timestamp_to_dt(ts: int) -> datetime:
    """Unix 时间戳转 datetime"""
    return datetime.fromtimestamp(ts, tz=timezone.utc)


def build_calendar(events: Iterable[GameEvent], filters: set[EventType] | None = None) -> bytes:
    """将事件列表构建为 .ics 日历文件内容

    Args:
        events: 游戏事件列表
        filters: 事件类型筛选集合，None 表示全部包含

    Returns:
        .ics 文件的字节内容
    """
    cal = Calendar()
    cal.add("prodid", PRODID)
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("x-wr-calname", CAL_NAME)

    for event in events:
        if filters and event.event_type not in filters:
            continue

        vevent = Event()
        vevent.add("uid", _make_uid(event))
        vevent.add("summary", event.title)
        vevent.add("dtstart", _timestamp_to_dt(event.start_at))
        vevent.add("dtend", _timestamp_to_dt(event.end_at))

        # 分类标签
        category_map = {
            EventType.ASSAULT: "总力战",
            EventType.EVENT: "活动",
            EventType.CARD: "卡池",
        }
        vevent.add("categories", [category_map.get(event.event_type, "其他")])
        vevent.add("description", f"[{category_map.get(event.event_type, '其他')}] {event.title}")

        cal.add_component(vevent)

    return cal.to_ical()
