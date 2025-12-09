"""
抖音直播AIGC后台 - 主入口

启动命令:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import asynccontextmanager
from typing import Dict, List, Optional
from loguru import logger
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings
from app.models.database import init_db
from app.api import api_router
from app.games.base import game_engine, GameEvent
from app.games.story_game import AIStoryGame
from app.games.puzzle_game import AIPuzzleGame
from app.core.danmu_collector import DanmuCollector, ThirdPartyCollector
from app.services.ai_service import AIService
from app.models.schemas import DanmuMessage, GiftMessage


# ==================== 房间管理器 ====================

class RoomManager:
    """直播间管理器"""
    
    def __init__(self):
        self._collectors: Dict[str, DanmuCollector] = {}
        self._ai_service: Optional[AIService] = None
        
    def set_ai_service(self, ai_service: AIService):
        """设置AI服务"""
        self._ai_service = ai_service
        game_engine.set_ai_service(ai_service)
        
    async def start_room(self, room_id: str, collector_type: str = "default") -> bool:
        """启动直播间采集"""
        if room_id in self._collectors:
            logger.warning(f"直播间已在运行: {room_id}")
            return False
            
        # 创建采集器
        if collector_type == "third_party":
            collector = ThirdPartyCollector(
                room_id=room_id,
                api_url=settings.DOUYIN_LIVE_WS_URL
            )
        else:
            collector = DanmuCollector(room_id)
            
        # 注册回调
        collector.on("chat", lambda msg: self._on_danmu(room_id, msg))
        collector.on("gift", lambda msg: self._on_gift(room_id, msg))
        
        self._collectors[room_id] = collector
        await collector.start()
        
        logger.info(f"启动直播间: {room_id}")
        return True
        
    async def stop_room(self, room_id: str):
        """停止直播间采集"""
        collector = self._collectors.get(room_id)
        if collector:
            await collector.stop()
            del self._collectors[room_id]
            logger.info(f"停止直播间: {room_id}")
            
    async def _on_danmu(self, room_id: str, message: DanmuMessage):
        """弹幕回调"""
        # 转发到游戏引擎
        await game_engine.handle_danmu(room_id, message)
        
        # WebSocket推送
        from app.api.routes.websocket import push_danmu
        await push_danmu(room_id, message.model_dump())
        
    async def _on_gift(self, room_id: str, gift: GiftMessage):
        """礼物回调"""
        # 转发到游戏引擎
        await game_engine.handle_gift(room_id, gift)
        
        # WebSocket推送
        from app.api.routes.websocket import push_gift
        await push_gift(room_id, gift.model_dump())
        
    async def inject_message(self, room_id: str, message: DanmuMessage) -> bool:
        """注入弹幕消息 (测试用)"""
        collector = self._collectors.get(room_id)
        if collector:
            await collector.inject_message(message)
            return True
        return False
        
    async def inject_gift(self, room_id: str, gift: GiftMessage) -> bool:
        """注入礼物消息 (测试用)"""
        collector = self._collectors.get(room_id)
        if collector:
            await collector.inject_gift(gift)
            return True
        return False
        
    def get_recent_messages(self, room_id: str, count: int = 50) -> List[DanmuMessage]:
        """获取最近消息"""
        collector = self._collectors.get(room_id)
        if collector:
            return collector.get_recent_messages(count)
        return []
        
    def get_room_status(self, room_id: str) -> Dict:
        """获取房间状态"""
        collector = self._collectors.get(room_id)
        return {
            "running": collector is not None and collector.is_running,
            "room_id": room_id
        }
        
    def get_all_rooms(self) -> List[Dict]:
        """获取所有房间"""
        return [
            {
                "room_id": room_id,
                "running": collector.is_running
            }
            for room_id, collector in self._collectors.items()
        ]


# 全局房间管理器
room_manager = RoomManager()


# ==================== 应用生命周期 ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("启动抖音直播AIGC后台...")
    
    # 初始化数据库
    await init_db()
    logger.info("数据库初始化完成")
    
    # 初始化AI服务
    ai_service = AIService()
    room_manager.set_ai_service(ai_service)
    logger.info("AI服务初始化完成")
    
    # 注册游戏
    game_engine.register(AIStoryGame)
    game_engine.register(AIPuzzleGame)
    logger.info(f"已注册游戏: {[g['name'] for g in game_engine.get_game_types()]}")
    
    yield
    
    # 清理
    logger.info("关闭抖音直播AIGC后台...")
    for room_id in list(room_manager._collectors.keys()):
        await room_manager.stop_room(room_id)


# ==================== 创建应用 ====================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## 抖音直播AIGC后台系统

### 功能特性:
- 🎮 多种AIGC游戏支持 (AI小说、AI解谜等)
- 💬 实时弹幕采集与处理
- 🎁 礼物/打赏事件处理
- 🗳️ 投票系统
- 📝 可配置的正则规则
- 🔌 WebSocket实时推送

### API分组:
- **/api/rooms** - 直播间管理
- **/api/games** - 游戏管理
- **/api/rules** - 规则配置
- **/api/danmu** - 弹幕管理
- **/api/ws** - WebSocket连接
""",
    lifespan=lifespan
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(api_router, prefix="/api")


# ==================== 基础路由 ====================

@app.get("/", response_class=HTMLResponse)
async def root():
    """首页"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>抖音直播AIGC后台</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 40px 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            .container {
                background: white;
                border-radius: 16px;
                padding: 40px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }
            h1 {
                color: #667eea;
                margin-bottom: 10px;
            }
            .subtitle {
                color: #666;
                margin-bottom: 30px;
            }
            .feature {
                background: #f8f9fa;
                padding: 15px 20px;
                border-radius: 8px;
                margin: 10px 0;
                border-left: 4px solid #667eea;
            }
            .links {
                margin-top: 30px;
            }
            a {
                display: inline-block;
                background: #667eea;
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                text-decoration: none;
                margin: 5px;
                transition: transform 0.2s;
            }
            a:hover {
                transform: translateY(-2px);
                background: #5a6fd6;
            }
            .code {
                background: #1e1e1e;
                color: #d4d4d4;
                padding: 15px;
                border-radius: 8px;
                font-family: 'Fira Code', monospace;
                font-size: 14px;
                overflow-x: auto;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎮 抖音直播AIGC后台</h1>
            <p class="subtitle">支持接入各种娱乐AIGC游戏的直播后台系统</p>
            
            <div class="feature">
                <strong>🎭 AI小说直播</strong> - AI生成互动故事，观众投票决定剧情
            </div>
            <div class="feature">
                <strong>🧩 AI解谜游戏</strong> - AI出题，观众投票答题，积分排名
            </div>
            <div class="feature">
                <strong>💬 弹幕采集</strong> - 实时采集弹幕，正则匹配，关键词触发
            </div>
            <div class="feature">
                <strong>🎁 礼物处理</strong> - 打赏识别，VIP加权，特殊事件触发
            </div>
            
            <div class="links">
                <a href="/docs">📚 API文档</a>
                <a href="/redoc">📖 ReDoc</a>
                <a href="/api/games/types">🎮 游戏类型</a>
            </div>
            
            <h3 style="margin-top: 30px;">快速开始</h3>
            <div class="code">
# 1. 创建直播间<br>
POST /api/rooms<br>
{"room_id": "123456", "name": "测试直播间"}<br><br>
# 2. 创建游戏<br>
POST /api/games/create<br>
{"room_id": "123456", "game_type": "story"}<br><br>
# 3. 启动游戏<br>
POST /api/games/123456/start
            </div>
        </div>
    </body>
    </html>
    """
    return html


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    logger.error(f"未处理异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc) if settings.DEBUG else "服务器内部错误"
        }
    )


# ==================== 启动入口 ====================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
