"""
API路由模块
"""
from fastapi import APIRouter
from .routes import rooms, games, rules, danmu, websocket

api_router = APIRouter()

# 注册路由
api_router.include_router(rooms.router, prefix="/rooms", tags=["直播间管理"])
api_router.include_router(games.router, prefix="/games", tags=["游戏管理"])
api_router.include_router(rules.router, prefix="/rules", tags=["规则配置"])
api_router.include_router(danmu.router, prefix="/danmu", tags=["弹幕管理"])
api_router.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])

__all__ = ["api_router"]
