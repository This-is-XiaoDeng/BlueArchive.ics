# 📅 BlueArchive.ics

将《蔚蓝档案》（Blue Archive）的卡池和活动信息转换为 [iCalendar](https://en.wikipedia.org/wiki/ICalendar) (.ics) 日历文件的 HTTP 服务。

## ✨ 功能

- 从 [GameKee](https://www.gamekee.com/) 自动采集以下事件：
  - **总力战 / 大决战**（assault）
  - **常规活动**（event）
  - **卡池**（card）
- 支持三个区服：国服（cn）、国际服（in）、日服（jp）
- 返回标准 .ics 日历文件，可导入 Google Calendar、Apple Calendar 等任意日历应用
- 支持按事件类型筛选

## 🚀 快速开始

### 环境要求

- Python >= 3.10
- [Poetry](https://python-poetry.org/)

### 安装与运行

```bash
# 克隆仓库
git clone https://github.com/This-is-XiaoDeng/BlueArchive.ics.git
cd BlueArchive.ics

# 安装依赖
poetry install

# 启动服务
poetry run uvicorn bluearchive_ics.main:app --host 0.0.0.0 --port 8000
```

服务启动后访问 `http://localhost:8000` 查看首页。

## 📋 API 文档

### `GET /`

项目首页，展示基本信息和使用说明。

### `GET /ba.ics`

返回 .ics 日历文件。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `server` | string | ❌ | 区服：`cn`（国服，默认）、`in`（国际服）、`jp`（日服） |
| `filter` | string | ❌ | 事件类型筛选，可重复提供。可选值：`assault`、`event`、`card`。不提供则返回全部类型 |

### 请求示例

```
GET /ba.ics
GET /ba.ics?server=jp
GET /ba.ics?server=cn&filter=event&filter=card
GET /ba.ics?server=in&filter=assault
```

### 日历订阅

大多数日历应用支持通过 URL 订阅 .ics 文件，将以下链接添加到你的日历应用中即可自动同步：

```
https://your-domain.com/ba.ics?server=jp
```

## 🔧 数据来源

数据采集自 [GameKee](https://www.gamekee.com/) 蔚蓝档案专区，参考了 [Moonlark](https://github.com/Moonlark-Dev/Moonlark) 项目的实现。

## 📄 许可证

本项目基于 [AGPL-3.0](LICENSE) 许可证开源。

```
BlueArchive.ics - 蔚蓝档案活动日历服务
Copyright (C) 2026  This-is-XiaoDeng

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
```
