"""
游戏管理API
"""
from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.games.base import game_engine
from app.models.schemas import GameType, GameSessionCreate

router = APIRouter()


class GameCreateRequest(BaseModel):
    """创建游戏请求"""
    room_id: str
    game_type: GameType
    config: Dict[str, Any] = {}


class GameActionRequest(BaseModel):
    """游戏动作请求"""
    action: str  # start, stop, pause, resume
    params: Dict[str, Any] = {}


@router.get("/types")
async def list_game_types():
    """获取支持的游戏类型"""
    return {
        "game_types": game_engine.get_game_types()
    }


@router.get("/active")
async def list_active_games():
    """获取所有活跃游戏"""
    return {
        "active_games": game_engine.get_active_games()
    }


@router.post("/create")
async def create_game(request: GameCreateRequest):
    """创建游戏"""
    game = await game_engine.create_game(
        room_id=request.room_id,
        game_type=request.game_type.value,
        config=request.config
    )
    
    if not game:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"创建游戏失败，未知类型: {request.game_type}"
        )
        
    return {
        "message": "游戏创建成功",
        "room_id": request.room_id,
        "game_type": request.game_type.value,
        "state": game.get_state()
    }


@router.post("/{room_id}/start")
async def start_game(room_id: str):
    """启动游戏"""
    success = await game_engine.start_game(room_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"启动游戏失败: {room_id}"
        )
        
    game = game_engine.get_game(room_id)
    
    return {
        "message": "游戏已启动",
        "room_id": room_id,
        "state": game.get_state() if game else {}
    }


@router.post("/{room_id}/stop")
async def stop_game(room_id: str):
    """停止游戏"""
    result = await game_engine.stop_game(room_id)
    
    return {
        "message": "游戏已停止",
        "room_id": room_id,
        "result": result
    }


@router.post("/{room_id}/pause")
async def pause_game(room_id: str):
    """暂停游戏"""
    game = game_engine.get_game(room_id)
    
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"游戏不存在: {room_id}"
        )
        
    await game.pause()
    
    return {
        "message": "游戏已暂停",
        "room_id": room_id,
        "state": game.get_state()
    }


@router.post("/{room_id}/resume")
async def resume_game(room_id: str):
    """恢复游戏"""
    game = game_engine.get_game(room_id)
    
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"游戏不存在: {room_id}"
        )
        
    await game.resume()
    
    return {
        "message": "游戏已恢复",
        "room_id": room_id,
        "state": game.get_state()
    }


@router.get("/{room_id}/state")
async def get_game_state(room_id: str):
    """获取游戏状态"""
    game = game_engine.get_game(room_id)
    
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"游戏不存在: {room_id}"
        )
        
    return {
        "room_id": room_id,
        "state": game.get_state()
    }


@router.post("/{room_id}/config")
async def update_game_config(room_id: str, config: Dict[str, Any]):
    """更新游戏配置"""
    game = game_engine.get_game(room_id)
    
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"游戏不存在: {room_id}"
        )
        
    game.config.update(config)
    
    return {
        "message": "配置已更新",
        "room_id": room_id,
        "config": game.config
    }


# ==================== 特定游戏API ====================

@router.get("/{room_id}/story/chapter")
async def get_current_chapter(room_id: str):
    """获取当前故事章节 (AI小说游戏)"""
    game = game_engine.get_game(room_id)
    
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"游戏不存在: {room_id}"
        )
        
    if game.game_type != "story":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不是小说游戏"
        )
        
    return {
        "chapter": game.get_current_chapter()
    }


@router.get("/{room_id}/puzzle/current")
async def get_current_puzzle(room_id: str):
    """获取当前谜题 (解谜游戏)"""
    game = game_engine.get_game(room_id)
    
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"游戏不存在: {room_id}"
        )
        
    if game.game_type != "puzzle":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不是解谜游戏"
        )
        
    return {
        "puzzle": game.get_current_puzzle()
    }


@router.get("/{room_id}/puzzle/leaderboard")
async def get_leaderboard(room_id: str, top_n: int = 10):
    """获取排行榜 (解谜游戏)"""
    game = game_engine.get_game(room_id)
    
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"游戏不存在: {room_id}"
        )
        
    if game.game_type != "puzzle":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不是解谜游戏"
        )
        
    return {
        "leaderboard": game.get_leaderboard(top_n)
    }


@router.get("/{room_id}/vote")
async def get_vote_status(room_id: str):
    """获取投票状态"""
    game = game_engine.get_game(room_id)
    
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"游戏不存在: {room_id}"
        )
        
    return {
        "vote_status": game.vote_manager.get_room_results(room_id)
    }
