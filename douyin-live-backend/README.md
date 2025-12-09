# 🎮 抖音直播AIGC后台系统

一个可扩展的抖音直播后台系统，支持接入各种AIGC娱乐游戏，包括AI小说直播、AI解谜游戏等。

## ✨ 功能特性

### 🎭 游戏支持
- **AI小说直播** - AI生成连续故事，观众投票决定剧情走向
- **AI解谜游戏** - AI生成谜题，观众投票选择答案，积分排名
- **可扩展架构** - 轻松添加新游戏类型

### 💬 弹幕处理
- 实时弹幕采集
- 正则表达式匹配
- 关键词触发
- 命令解析

### 🗳️ 投票系统
- 支持数字投票 (1, 2, 3...)
- 支持文字投票 (选1, 投2, A, B...)
- VIP/礼物用户加权投票
- 可配置投票时间窗口

### 🎁 礼物处理
- 打赏消息识别
- 礼物触发特殊事件
- VIP用户识别

### 🔌 实时推送
- WebSocket实时数据流
- 游戏状态更新
- 投票实时统计

## 🚀 快速开始

### 1. 安装依赖

```bash
cd douyin-live-backend
pip install -r requirements.txt
```

### 2. 配置环境

```bash
cp .env.example .env
# 编辑 .env 文件，配置你的 OpenAI API Key 等信息
```

### 3. 启动服务

```bash
# 开发模式
python -m app.main

# 或使用 uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问服务

- 首页: http://localhost:8000
- API文档: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📚 API使用示例

### 创建直播间

```bash
curl -X POST "http://localhost:8000/api/rooms" \
  -H "Content-Type: application/json" \
  -d '{"room_id": "123456", "name": "我的直播间"}'
```

### 创建AI小说游戏

```bash
curl -X POST "http://localhost:8000/api/games/create" \
  -H "Content-Type: application/json" \
  -d '{
    "room_id": "123456",
    "game_type": "story",
    "config": {
      "style": "悬疑",
      "title": "神秘事件",
      "vote_duration": 30
    }
  }'
```

### 启动游戏

```bash
curl -X POST "http://localhost:8000/api/games/123456/start"
```

### 注入测试弹幕

```bash
curl -X POST "http://localhost:8000/api/danmu/inject" \
  -H "Content-Type: application/json" \
  -d '{
    "room_id": "123456",
    "username": "测试用户",
    "content": "1"
  }'
```

### WebSocket连接

```javascript
const ws = new WebSocket('ws://localhost:8000/api/ws/room/123456');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('收到消息:', data);
};

// 注入测试弹幕
ws.send(JSON.stringify({
  type: 'inject_danmu',
  data: {
    username: '测试',
    content: '选1'
  }
}));
```

## 🎮 游戏类型

### AI小说直播 (story)

观众参与式互动小说，AI根据观众选择生成后续剧情。

**配置项:**
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| style | string | "悬疑" | 故事风格 |
| title | string | "神秘故事" | 故事标题 |
| vote_duration | int | 30 | 投票时间(秒) |
| min_votes | int | 3 | 最小投票数 |
| auto_continue | bool | true | 自动继续 |
| gift_influence | bool | true | 礼物影响剧情 |
| max_chapters | int | 50 | 最大章节数 |

**玩法:**
1. AI生成故事开头，提供2-3个选项
2. 观众在投票时间内发送 "1", "2", "3" 或 "选1", "选2" 等投票
3. 投票结束后，AI根据结果生成下一章
4. 打赏用户可以在留言中添加剧情元素

### AI解谜游戏 (puzzle)

AI出题，观众答题，积分排名。

**配置项:**
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| theme | string | "综合" | 谜题主题 |
| difficulty | string | "medium" | 难度(easy/medium/hard) |
| vote_duration | int | 20 | 投票时间(秒) |
| puzzle_count | int | 10 | 谜题数量 |
| points_per_correct | int | 10 | 正确得分 |
| streak_bonus | int | 5 | 连续正确奖励 |
| vip_weight | float | 2.0 | VIP投票权重 |

**玩法:**
1. AI生成选择题
2. 观众发送选项编号投票
3. 票数最高的选项作为最终答案
4. 答对获得积分，连续答对有额外奖励
5. 礼物用户获得投票加权

## 📝 规则配置

### 投票规则

```bash
# 添加投票规则
curl -X POST "http://localhost:8000/api/rules" \
  -H "Content-Type: application/json" \
  -d '{
    "room_id": "123456",
    "rule_type": "vote",
    "pattern": "^[1-9]$",
    "action": "vote"
  }'
```

### 关键词规则

```bash
# 添加关键词规则
curl -X POST "http://localhost:8000/api/rules" \
  -H "Content-Type: application/json" \
  -d '{
    "room_id": "123456",
    "rule_type": "keyword",
    "pattern": "继续|下一个",
    "action": "continue"
  }'
```

### 测试正则表达式

```bash
curl -X POST "http://localhost:8000/api/rules/test" \
  -H "Content-Type: application/json" \
  -d '{
    "pattern": "^[选投][1-9]$",
    "test_text": "选2"
  }'
```

## 🏗️ 项目结构

```
douyin-live-backend/
├── app/
│   ├── api/                 # API路由
│   │   └── routes/
│   │       ├── rooms.py     # 直播间管理
│   │       ├── games.py     # 游戏管理
│   │       ├── rules.py     # 规则配置
│   │       ├── danmu.py     # 弹幕管理
│   │       └── websocket.py # WebSocket
│   ├── core/                # 核心模块
│   │   ├── danmu_collector.py    # 弹幕采集
│   │   ├── message_processor.py  # 消息处理
│   │   └── vote_manager.py       # 投票管理
│   ├── games/               # 游戏模块
│   │   ├── base.py          # 游戏基类
│   │   ├── story_game.py    # AI小说游戏
│   │   └── puzzle_game.py   # AI解谜游戏
│   ├── models/              # 数据模型
│   │   ├── database.py      # 数据库模型
│   │   └── schemas.py       # Pydantic模式
│   ├── services/            # 服务模块
│   │   └── ai_service.py    # AI服务
│   └── main.py              # 主入口
├── config/
│   └── settings.py          # 配置文件
├── data/                    # 数据目录
├── logs/                    # 日志目录
├── requirements.txt         # 依赖
└── README.md
```

## 🔧 扩展开发

### 添加新游戏类型

1. 创建游戏类，继承 `BaseGame`:

```python
from app.games.base import BaseGame, GameEvent

class MyNewGame(BaseGame):
    game_type = "my_game"
    game_name = "我的游戏"
    game_description = "游戏描述"
    
    async def on_start(self):
        # 游戏启动逻辑
        pass
    
    async def on_stop(self):
        # 游戏停止逻辑
        return {"result": "data"}
    
    async def on_danmu(self, message):
        # 处理弹幕
        pass
    
    async def on_gift(self, gift, processed):
        # 处理礼物
        pass
```

2. 注册游戏:

```python
from app.games.base import game_engine
from my_game import MyNewGame

game_engine.register(MyNewGame)
```

### 添加自定义弹幕源

```python
from app.core.danmu_collector import DanmuCollector

class MyCollector(DanmuCollector):
    async def _connect_and_collect(self):
        # 实现你的采集逻辑
        pass
```

## 🔒 安全注意

- 生产环境请修改 `SECRET_KEY`
- 不要在代码中硬编码 API Key
- 建议使用 HTTPS
- 适当配置 CORS

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request!
