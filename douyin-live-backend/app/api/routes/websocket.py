"""
WebSocket API

提供实时数据推送:
- 弹幕实时流
- 游戏状态更新
- 投票实时统计
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Dict, Set, Any
import asyncio
import json
from datetime import datetime
from loguru import logger

router = APIRouter()


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # room_id -> set of connections
        self.room_connections: Dict[str, Set[WebSocket]] = {}
        # 全局连接
        self.global_connections: Set[WebSocket] = set()
        
    async def connect(self, websocket: WebSocket, room_id: str = None):
        """建立连接"""
        await websocket.accept()
        
        if room_id:
            if room_id not in self.room_connections:
                self.room_connections[room_id] = set()
            self.room_connections[room_id].add(websocket)
        else:
            self.global_connections.add(websocket)
            
        logger.info(f"WebSocket连接建立: room={room_id}")
        
    def disconnect(self, websocket: WebSocket, room_id: str = None):
        """断开连接"""
        if room_id and room_id in self.room_connections:
            self.room_connections[room_id].discard(websocket)
        else:
            self.global_connections.discard(websocket)
            
        logger.info(f"WebSocket连接断开: room={room_id}")
        
    async def send_to_room(self, room_id: str, message: Dict[str, Any]):
        """发送消息到房间"""
        connections = self.room_connections.get(room_id, set())
        dead_connections = set()
        
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.add(connection)
                
        # 清理断开的连接
        for conn in dead_connections:
            self.room_connections[room_id].discard(conn)
            
    async def broadcast(self, message: Dict[str, Any]):
        """广播消息到所有连接"""
        dead_connections = set()
        
        for connection in self.global_connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.add(connection)
                
        # 清理断开的连接
        for conn in dead_connections:
            self.global_connections.discard(conn)
            
    async def send_personal(self, websocket: WebSocket, message: Dict[str, Any]):
        """发送个人消息"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"发送消息失败: {e}")


# 全局连接管理器
manager = ConnectionManager()


@router.websocket("/room/{room_id}")
async def room_websocket(
    websocket: WebSocket,
    room_id: str
):
    """
    直播间WebSocket
    
    接收:
    - 弹幕实时流
    - 游戏状态更新
    - 投票统计
    """
    await manager.connect(websocket, room_id)
    
    try:
        # 发送连接成功消息
        await manager.send_personal(websocket, {
            "type": "connected",
            "room_id": room_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await handle_client_message(websocket, room_id, message)
            except json.JSONDecodeError:
                await manager.send_personal(websocket, {
                    "type": "error",
                    "message": "无效的JSON格式"
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)


@router.websocket("/global")
async def global_websocket(websocket: WebSocket):
    """
    全局WebSocket
    
    接收所有房间的事件
    """
    await manager.connect(websocket)
    
    try:
        await manager.send_personal(websocket, {
            "type": "connected",
            "scope": "global",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await handle_global_message(websocket, message)
            except json.JSONDecodeError:
                await manager.send_personal(websocket, {
                    "type": "error",
                    "message": "无效的JSON格式"
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def handle_client_message(
    websocket: WebSocket,
    room_id: str,
    message: Dict[str, Any]
):
    """处理客户端消息"""
    msg_type = message.get("type", "")
    
    if msg_type == "ping":
        await manager.send_personal(websocket, {
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat()
        })
        
    elif msg_type == "subscribe":
        # 订阅特定事件
        events = message.get("events", [])
        await manager.send_personal(websocket, {
            "type": "subscribed",
            "events": events
        })
        
    elif msg_type == "inject_danmu":
        # 注入测试弹幕 (调试用)
        from app.main import room_manager
        from app.models.schemas import DanmuMessage, MessageType
        
        danmu_data = message.get("data", {})
        msg = DanmuMessage(
            room_id=room_id,
            user_id=danmu_data.get("user_id", "ws_test"),
            username=danmu_data.get("username", "WS测试"),
            content=danmu_data.get("content", ""),
            msg_type=MessageType.CHAT
        )
        
        await room_manager.inject_message(room_id, msg)
        
        await manager.send_personal(websocket, {
            "type": "inject_result",
            "success": True
        })
        
    elif msg_type == "get_state":
        # 获取游戏状态
        from app.games.base import game_engine
        
        game = game_engine.get_game(room_id)
        state = game.get_state() if game else None
        
        await manager.send_personal(websocket, {
            "type": "game_state",
            "room_id": room_id,
            "state": state
        })


async def handle_global_message(
    websocket: WebSocket,
    message: Dict[str, Any]
):
    """处理全局消息"""
    msg_type = message.get("type", "")
    
    if msg_type == "ping":
        await manager.send_personal(websocket, {
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat()
        })
        
    elif msg_type == "list_rooms":
        from app.main import room_manager
        
        rooms = room_manager.get_all_rooms()
        
        await manager.send_personal(websocket, {
            "type": "room_list",
            "rooms": rooms
        })


# ==================== 事件推送接口 ====================

async def push_danmu(room_id: str, danmu: Dict[str, Any]):
    """推送弹幕"""
    await manager.send_to_room(room_id, {
        "type": "danmu",
        "room_id": room_id,
        "data": danmu,
        "timestamp": datetime.utcnow().isoformat()
    })


async def push_gift(room_id: str, gift: Dict[str, Any]):
    """推送礼物"""
    await manager.send_to_room(room_id, {
        "type": "gift",
        "room_id": room_id,
        "data": gift,
        "timestamp": datetime.utcnow().isoformat()
    })


async def push_game_event(room_id: str, event_type: str, data: Any):
    """推送游戏事件"""
    await manager.send_to_room(room_id, {
        "type": "game_event",
        "event": event_type,
        "room_id": room_id,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    })


async def push_vote_update(room_id: str, vote_data: Dict[str, Any]):
    """推送投票更新"""
    await manager.send_to_room(room_id, {
        "type": "vote_update",
        "room_id": room_id,
        "data": vote_data,
        "timestamp": datetime.utcnow().isoformat()
    })
