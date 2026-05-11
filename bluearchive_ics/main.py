"""FastAPI 主应用"""

from __future__ import annotations

from enum import Enum
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


class ServerType(str, Enum):
    CN = "cn"
    IN = "in"
    JP = "jp"


INDEX_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BlueArchive.ics</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh; display: flex; align-items: center; justify-content: center;
    color: #333;
  }
  .card {
    background: white; border-radius: 16px; padding: 48px;
    max-width: 640px; width: 90%; box-shadow: 0 20px 60px rgba(0,0,0,0.3);
  }
  h1 { font-size: 2em; margin-bottom: 8px; color: #4a56e2; }
  .subtitle { color: #666; margin-bottom: 24px; font-size: 1.1em; }
  h2 { font-size: 1.2em; margin: 24px 0 12px; color: #4a56e2; }
  p, li { line-height: 1.7; margin-bottom: 8px; }
  code {
    background: #f0f0f5; padding: 2px 8px; border-radius: 4px;
    font-family: "Fira Code", "Consolas", monospace; font-size: 0.9em;
  }
  pre {
    background: #f0f0f5; padding: 16px; border-radius: 8px;
    overflow-x: auto; margin: 12px 0; font-size: 0.9em;
  }
  a { color: #4a56e2; text-decoration: none; }
  a:hover { text-decoration: underline; }
  .badge {
    display: inline-block; background: #4a56e2; color: white;
    padding: 4px 12px; border-radius: 20px; font-size: 0.85em; margin-right: 8px;
  }
  ul { padding-left: 20px; }
</style>
</head>
<body>
<div class="card">
  <h1>📅 BlueArchive.ics</h1>
  <p class="subtitle">蔚蓝档案活动日历订阅服务</p>

  <p>将《蔚蓝档案》的<strong>卡池</strong>、<strong>活动</strong>和<strong>总力战</strong>信息转换为标准 iCalendar (.ics) 日历文件，可导入任何日历应用。</p>

  <h2>🚀 使用方法</h2>
  <p>订阅日历链接：</p>
  <pre><code>GET /ba.ics?server={server}&amp;filter={type}</code></pre>

  <h2>📋 参数说明</h2>
  <ul>
    <li><code>server</code>（可选，默认 <code>cn</code>）：<code>cn</code> 国服 / <code>in</code> 国际服 / <code>jp</code> 日服</li>
    <li><code>filter</code>（可选，可重复）：<code>assault</code> 总力战 / <code>event</code> 活动 / <code>card</code> 卡池</li>
  </ul>

  <h2>💡 示例</h2>
  <pre><code>/ba.ics?server=jp
/ba.ics?server=cn&amp;filter=event&amp;filter=card
/ba.ics?server=in&amp;filter=assault</code></pre>

  <h2>📖 开源</h2>
  <p>
    <span class="badge">AGPL-3.0</span>
    <a href="https://github.com/This-is-XiaoDeng/BlueArchive.ics" target="_blank">GitHub 仓库</a>
  </p>
</div>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def index():
    """项目首页"""
    return INDEX_HTML


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
