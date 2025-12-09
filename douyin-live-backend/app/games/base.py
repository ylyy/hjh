"""
游戏引擎基类

提供:
1. 可插拔的游戏框架
2. 统一的事件处理接口
3. 游戏状态管理
4. AI服务集成
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable, Type
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
from loguru import logger

from app.models.schemas import DanmuMessage, GiftMessage, GameType, GameStatus
from app.core.message_processor import MessageProcessor, ProcessedMessage
from app.core.vote_manager import VoteManager
from app.services.ai_service import AIService


class GameEvent(str, Enum):
    """游戏事件类型"""
    STARTED = "started"
    PAUSED = "paused"
    RESUMED = "resumed"
    ENDED = "ended"
    STATE_CHANGED = "state_changed"
    ACTION_TRIGGERED = "action_triggered"
    VOTE_STARTED = "vote_started"
    VOTE_ENDED = "vote_ended"
    AI_GENERATED = "ai_generated"
    ERROR = "error"


@dataclass
class GameContext:
    """游戏上下文"""
    room_id: str
    game_type: str
    session_id: str
    config: Dict[str, Any] = field(default_factory=dict)
    state: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.utcnow)
    
    def update_state(self, key: str, value: Any):
        """更新状态"""
        self.state[key] = value
        
    def add_history(self, event_type: str, data: Any):
        """添加历史记录"""
        self.history.append({
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        })


class BaseGame(ABC):
    """
    游戏基类
    
    所有游戏插件都需要继承此类
    """
    
    # 游戏类型标识
    game_type: str = "base"
    game_name: str = "基础游戏"
    game_description: str = "游戏基类"
    
    def __init__(
        self,
        room_id: str,
        config: Dict[str, Any] = None,
        ai_service: AIService = None,
        vote_manager: VoteManager = None,
        message_processor: MessageProcessor = None
    ):
        self.room_id = room_id
        self.config = config or {}
        self.ai_service = ai_service
        self.vote_manager = vote_manager or VoteManager()
        self.message_processor = message_processor or MessageProcessor()
        
        self.status = GameStatus.WAITING
        self.context: Optional[GameContext] = None
        
        self._callbacks: Dict[str, List[Callable]] = {}
        self._setup_default_rules()
        
    def _setup_default_rules(self):
        """设置默认规则"""
        pass
    
    def on(self, event: GameEvent, callback: Callable):
        """注册事件回调"""
        event_key = event.value if isinstance(event, GameEvent) else event
        if event_key not in self._callbacks:
            self._callbacks[event_key] = []
        self._callbacks[event_key].append(callback)
        
    async def emit(self, event: GameEvent, data: Any = None):
        """触发事件"""
        event_key = event.value if isinstance(event, GameEvent) else event
        for callback in self._callbacks.get(event_key, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                logger.error(f"游戏回调错误: {e}")
    
    async def start(self, session_id: str = None) -> bool:
        """
        启动游戏
        
        Args:
            session_id: 会话ID (可选)
            
        Returns:
            是否成功
        """
        if self.status == GameStatus.ACTIVE:
            logger.warning(f"游戏已在运行: {self.room_id}")
            return False
            
        import uuid
        session_id = session_id or str(uuid.uuid4())[:8]
        
        self.context = GameContext(
            room_id=self.room_id,
            game_type=self.game_type,
            session_id=session_id,
            config=self.config
        )
        
        self.status = GameStatus.ACTIVE
        
        # 调用子类初始化
        await self.on_start()
        
        await self.emit(GameEvent.STARTED, {
            "room_id": self.room_id,
            "session_id": session_id,
            "game_type": self.game_type
        })
        
        logger.info(f"游戏启动: {self.game_type} - {self.room_id}")
        return True
    
    async def stop(self) -> Dict[str, Any]:
        """
        停止游戏
        
        Returns:
            游戏结果
        """
        if self.status != GameStatus.ACTIVE:
            return {}
            
        self.status = GameStatus.FINISHED
        
        # 调用子类清理
        result = await self.on_stop()
        
        await self.emit(GameEvent.ENDED, result)
        
        logger.info(f"游戏结束: {self.game_type} - {self.room_id}")
        return result
    
    async def pause(self):
        """暂停游戏"""
        if self.status == GameStatus.ACTIVE:
            self.status = GameStatus.PAUSED
            await self.on_pause()
            await self.emit(GameEvent.PAUSED)
            
    async def resume(self):
        """恢复游戏"""
        if self.status == GameStatus.PAUSED:
            self.status = GameStatus.ACTIVE
            await self.on_resume()
            await self.emit(GameEvent.RESUMED)
    
    async def handle_danmu(self, message: DanmuMessage):
        """
        处理弹幕消息
        
        Args:
            message: 弹幕消息
        """
        if self.status != GameStatus.ACTIVE:
            return
            
        # 处理消息
        processed = await self.message_processor.process(message)
        
        # 调用子类处理
        await self.on_danmu(processed)
        
    async def handle_gift(self, gift: GiftMessage):
        """
        处理礼物消息
        
        Args:
            gift: 礼物消息
        """
        if self.status != GameStatus.ACTIVE:
            return
            
        # 处理礼物
        result = await self.message_processor.process_gift(gift)
        
        # 调用子类处理
        await self.on_gift(gift, result)
    
    # ==================== 子类需要实现的方法 ====================
    
    @abstractmethod
    async def on_start(self):
        """游戏启动时调用"""
        pass
    
    @abstractmethod
    async def on_stop(self) -> Dict[str, Any]:
        """游戏停止时调用，返回游戏结果"""
        pass
    
    @abstractmethod
    async def on_danmu(self, message: ProcessedMessage):
        """处理弹幕"""
        pass
    
    @abstractmethod
    async def on_gift(self, gift: GiftMessage, processed: Dict):
        """处理礼物"""
        pass
    
    async def on_pause(self):
        """游戏暂停时调用"""
        pass
    
    async def on_resume(self):
        """游戏恢复时调用"""
        pass
    
    # ==================== 辅助方法 ====================
    
    def get_state(self) -> Dict[str, Any]:
        """获取游戏状态"""
        return {
            "status": self.status.value,
            "game_type": self.game_type,
            "room_id": self.room_id,
            "context": self.context.state if self.context else {},
            "config": self.config
        }
    
    async def update_state(self, updates: Dict[str, Any]):
        """更新游戏状态"""
        if self.context:
            for key, value in updates.items():
                self.context.update_state(key, value)
            await self.emit(GameEvent.STATE_CHANGED, self.context.state)


class GameEngine:
    """
    游戏引擎
    
    管理所有游戏实例:
    - 游戏注册
    - 游戏创建
    - 生命周期管理
    """
    
    def __init__(self):
        self._game_classes: Dict[str, Type[BaseGame]] = {}
        self._active_games: Dict[str, BaseGame] = {}  # room_id -> game
        self._ai_service: Optional[AIService] = None
        
    def set_ai_service(self, ai_service: AIService):
        """设置AI服务"""
        self._ai_service = ai_service
        
    def register(self, game_class: Type[BaseGame]):
        """
        注册游戏类
        
        Args:
            game_class: 游戏类
        """
        game_type = game_class.game_type
        self._game_classes[game_type] = game_class
        logger.info(f"注册游戏: {game_type} - {game_class.game_name}")
        
    def unregister(self, game_type: str):
        """注销游戏类"""
        if game_type in self._game_classes:
            del self._game_classes[game_type]
            
    def get_game_types(self) -> List[Dict[str, str]]:
        """获取所有已注册的游戏类型"""
        return [
            {
                "type": game_class.game_type,
                "name": game_class.game_name,
                "description": game_class.game_description
            }
            for game_class in self._game_classes.values()
        ]
    
    async def create_game(
        self,
        room_id: str,
        game_type: str,
        config: Dict[str, Any] = None
    ) -> Optional[BaseGame]:
        """
        创建游戏实例
        
        Args:
            room_id: 直播间ID
            game_type: 游戏类型
            config: 游戏配置
            
        Returns:
            游戏实例
        """
        # 停止现有游戏
        await self.stop_game(room_id)
        
        game_class = self._game_classes.get(game_type)
        if not game_class:
            logger.error(f"未知游戏类型: {game_type}")
            return None
            
        game = game_class(
            room_id=room_id,
            config=config,
            ai_service=self._ai_service
        )
        
        self._active_games[room_id] = game
        logger.info(f"创建游戏: {game_type} - {room_id}")
        
        return game
    
    async def start_game(self, room_id: str) -> bool:
        """启动游戏"""
        game = self._active_games.get(room_id)
        if game:
            return await game.start()
        return False
    
    async def stop_game(self, room_id: str) -> Optional[Dict]:
        """停止游戏"""
        game = self._active_games.get(room_id)
        if game:
            result = await game.stop()
            del self._active_games[room_id]
            return result
        return None
    
    def get_game(self, room_id: str) -> Optional[BaseGame]:
        """获取游戏实例"""
        return self._active_games.get(room_id)
    
    async def handle_danmu(self, room_id: str, message: DanmuMessage):
        """转发弹幕到游戏"""
        game = self._active_games.get(room_id)
        if game:
            await game.handle_danmu(message)
            
    async def handle_gift(self, room_id: str, gift: GiftMessage):
        """转发礼物到游戏"""
        game = self._active_games.get(room_id)
        if game:
            await game.handle_gift(gift)
    
    def get_active_games(self) -> Dict[str, Dict]:
        """获取所有活跃游戏"""
        return {
            room_id: game.get_state()
            for room_id, game in self._active_games.items()
        }


# 全局游戏引擎实例
game_engine = GameEngine()
