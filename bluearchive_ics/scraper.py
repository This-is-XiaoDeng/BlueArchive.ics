"""GameKee 数据采集模块"""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

import httpx

GAMEKEE_API_BASE = "https://www.gamekee.com/v1"
GAMEKEE_HEADERS = {"game-alias": "ba"}

SERVER_ID_MAP: dict[str, int] = {"cn": 16, "in": 17, "jp": 15}


class EventType(str, Enum):
    ASSAULT = "assault"
    EVENT = "event"
    CARD = "card"


@dataclass
class GameEvent:
    """游戏事件数据"""

    id: int
    title: str
    start_at: int
    end_at: int
    event_type: EventType
    picture: str = ""

    @property
    def is_active(self) -> bool:
        return self.end_at >= time.time()


async def _fetch_json(url: str, params: dict[str, Any] | None = None) -> dict:
    """请求 GameKee API 并返回 JSON"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url, params=params, headers=GAMEKEE_HEADERS)
        resp.raise_for_status()
        return resp.json()


async def fetch_card_pool(server_id: int) -> list[GameEvent]:
    """获取卡池数据"""
    url = f"{GAMEKEE_API_BASE}/cardPool/query-list"
    params = {
        "order_by": "-1",
        "card_tag_id": "",
        "keyword": "",
        "kind_id": "6",
        "status": "0",
        "serverId": str(server_id),
    }
    data = await _fetch_json(url, params)
    events: list[GameEvent] = []
    for item in data.get("data", []):
        if item.get("end_at", 0) < time.time():
            continue
        events.append(
            GameEvent(
                id=item.get("id", 0),
                title=item.get("name", "未知卡池"),
                start_at=item.get("start_at", 0),
                end_at=item.get("end_at", 0),
                event_type=EventType.CARD,
                picture=item.get("icon", ""),
            )
        )
    return events


async def fetch_activities(server_id: int) -> list[GameEvent]:
    """获取常规活动数据"""
    url = f"{GAMEKEE_API_BASE}/activity/page-list"
    params = {
        "importance": "0",
        "sort": "-1",
        "keyword": "",
        "limit": "999",
        "page_no": "1",
        "serverId": str(server_id),
        "status": "0",
    }
    data = await _fetch_json(url, params)
    events: list[GameEvent] = []
    for item in data.get("data", []):
        if item.get("end_at", 0) < time.time():
            continue
        events.append(
            GameEvent(
                id=item.get("id", 0),
                title=item.get("title", "未知活动"),
                start_at=item.get("begin_at", 0),
                end_at=item.get("end_at", 0),
                event_type=EventType.EVENT,
                picture=item.get("picture", ""),
            )
        )
    return events


async def fetch_total_assault(server_id: int) -> list[GameEvent]:
    """获取总力战/大决战数据"""
    url = f"{GAMEKEE_API_BASE}/activity/page-list"
    params = {
        "importance": "0",
        "sort": "-1",
        "keyword": "",
        "limit": "999",
        "page_no": "1",
        "serverId": str(server_id),
        "status": "0",
        "activity_kind_id": "15",
    }
    data = await _fetch_json(url, params)
    events: list[GameEvent] = []
    for item in data.get("data", []):
        if item.get("end_at", 0) < time.time():
            continue
        events.append(
            GameEvent(
                id=item.get("id", 0),
                title=item.get("title", "总力战"),
                start_at=item.get("begin_at", 0),
                end_at=item.get("end_at", 0),
                event_type=EventType.ASSAULT,
                picture=item.get("picture", ""),
            )
        )
    return events


async def fetch_all_events(server: str) -> list[GameEvent]:
    """获取指定服务器的全部事件"""
    if server not in SERVER_ID_MAP:
        raise ValueError(f"不支持的服务器: {server}，可选值: cn, in, jp")

    server_id = SERVER_ID_MAP[server]
    cards, activities, assaults = [], [], []

    # 并发请求三类数据
    async with httpx.AsyncClient(timeout=30.0) as _:
        import asyncio

        cards_task = fetch_card_pool(server_id)
        activities_task = fetch_activities(server_id)
        assault_task = fetch_total_assault(server_id)

        cards, activities, assaults = await asyncio.gather(
            cards_task, activities_task, assault_task
        )

    return assaults + activities + cards
