# 📅 BlueArchive.ics

将《蔚蓝档案》（Blue Archive）的卡池和活动信息转换为 [iCalendar](https://en.wikipedia.org/wiki/ICalendar) (.ics) 日历文件的 HTTP 服务。

## ✨ 功能

- 自动采集 **卡池**、**活动**、**总力战 / 大决战** 三类事件
- 支持 **国服 (cn)**、**国际服 (in)**、**日服 (jp)**
- 相同时间的卡池自动合并（可用 `/full-card-info.ics` 查看完整信息）
- 标准 .ics 格式，兼容 Google Calendar、Apple Calendar 等任意日历应用

## 🚀 快速开始

```bash
git clone https://github.com/This-is-XiaoDeng/BlueArchive.ics.git
cd BlueArchive.ics
poetry install
poetry run uvicorn bluearchive_ics.main:app --host 0.0.0.0 --port 8000
```

## 📋 路由一览

所有路径均可加 `/{server}/` 前缀（`cn` / `in` / `jp`），默认为国服 `cn`。

| 路径 | 内容 | 卡池合并 |
|------|------|---------|
| `/ba.ics` | 全部事件（兼容旧链接） | ✅ |
| `/all.ics` | 全部事件 | ✅ |
| `/card.ics` | 仅卡池 | ✅ |
| `/card/merged.ics` | 仅卡池（显式合并） | ✅ |
| `/full-card-info.ics` | 仅卡池（完整信息） | ❌ |
| `/assault.ics` | 仅总力战 | — |
| `/event.ics` | 仅活动 | — |

### 示例

```
GET /ba.ics                 # 国服全部
GET /jp/ba.ics              # 日服全部
GET /cn/card.ics            # 国服卡池（合并）
GET /cn/full-card-info.ics  # 国服卡池（完整）
GET /in/assault.ics         # 国际服总力战
```

### 日历订阅

将链接添加到日历应用即可自动同步：

```
https://your-domain.com/cn/ba.ics
https://your-domain.com/jp/ba.ics
```

## 🔧 数据来源

[GameKee](https://www.gamekee.com/) 蔚蓝档案专区，参考了 [Moonlark](https://github.com/Moonlark-Dev/Moonlark) 项目。

## 📄 许可证

[AGPL-3.0](LICENSE)
