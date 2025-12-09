"""
弹幕管理API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.models.database import get_db, DanmuRecord, GiftRecord
from app.models.schemas import DanmuMessage, GiftMessage, MessageType

router = APIRouter()


class DanmuInject(BaseModel):
    """注入弹幕请求"""
    room_id: str
    user_id: str = "test_user"
    username: str = "测试用户"
    content: str
    msg_type: str = "chat"


class GiftInject(BaseModel):
    """注入礼物请求"""
    room_id: str
    user_id: str = "test_user"
    username: str = "测试用户"
    gift_name: str
    gift_count: int = 1
    gift_value: float = 0
    message: Optional[str] = None


@router.get("/history")
async def get_danmu_history(
    room_id: str,
    msg_type: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = Query(default=100, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """获取弹幕历史"""
    query = select(DanmuRecord).filter(DanmuRecord.room_id == room_id)
    
    if msg_type:
        query = query.filter(DanmuRecord.msg_type == msg_type)
    if start_time:
        query = query.filter(DanmuRecord.created_at >= start_time)
    if end_time:
        query = query.filter(DanmuRecord.created_at <= end_time)
        
    query = query.order_by(DanmuRecord.created_at.desc()).limit(limit)
    result = await db.execute(query)
    records = result.scalars().all()
    
    return {
        "room_id": room_id,
        "count": len(records),
        "records": [
            {
                "id": r.id,
                "user_id": r.user_id,
                "username": r.username,
                "content": r.content,
                "msg_type": r.msg_type,
                "created_at": r.created_at.isoformat()
            }
            for r in records
        ]
    }


@router.get("/gifts")
async def get_gift_history(
    room_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    min_value: Optional[float] = None,
    limit: int = Query(default=100, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """获取礼物历史"""
    query = select(GiftRecord).filter(GiftRecord.room_id == room_id)
    
    if start_time:
        query = query.filter(GiftRecord.created_at >= start_time)
    if end_time:
        query = query.filter(GiftRecord.created_at <= end_time)
    if min_value:
        query = query.filter(GiftRecord.gift_value >= min_value)
        
    query = query.order_by(GiftRecord.created_at.desc()).limit(limit)
    result = await db.execute(query)
    records = result.scalars().all()
    
    return {
        "room_id": room_id,
        "count": len(records),
        "records": [
            {
                "id": r.id,
                "user_id": r.user_id,
                "username": r.username,
                "gift_name": r.gift_name,
                "gift_count": r.gift_count,
                "gift_value": r.gift_value,
                "message": r.message,
                "created_at": r.created_at.isoformat()
            }
            for r in records
        ]
    }


@router.get("/stats")
async def get_danmu_stats(
    room_id: str,
    hours: int = 24,
    db: AsyncSession = Depends(get_db)
):
    """获取弹幕统计"""
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    # 弹幕统计
    danmu_query = select(
        func.count(DanmuRecord.id).label("total"),
        func.count(func.distinct(DanmuRecord.user_id)).label("unique_users")
    ).filter(
        DanmuRecord.room_id == room_id,
        DanmuRecord.created_at >= start_time
    )
    danmu_result = await db.execute(danmu_query)
    danmu_stats = danmu_result.one()
    
    # 礼物统计
    gift_query = select(
        func.count(GiftRecord.id).label("total"),
        func.sum(GiftRecord.gift_value).label("total_value"),
        func.count(func.distinct(GiftRecord.user_id)).label("unique_gifters")
    ).filter(
        GiftRecord.room_id == room_id,
        GiftRecord.created_at >= start_time
    )
    gift_result = await db.execute(gift_query)
    gift_stats = gift_result.one()
    
    return {
        "room_id": room_id,
        "period_hours": hours,
        "danmu": {
            "total": danmu_stats.total or 0,
            "unique_users": danmu_stats.unique_users or 0
        },
        "gifts": {
            "total": gift_stats.total or 0,
            "total_value": float(gift_stats.total_value or 0),
            "unique_gifters": gift_stats.unique_gifters or 0
        }
    }


@router.post("/inject")
async def inject_danmu(data: DanmuInject):
    """
    注入测试弹幕
    
    用于测试游戏逻辑
    """
    from app.main import room_manager
    
    message = DanmuMessage(
        room_id=data.room_id,
        user_id=data.user_id,
        username=data.username,
        content=data.content,
        msg_type=MessageType(data.msg_type)
    )
    
    # 注入到采集器
    success = await room_manager.inject_message(data.room_id, message)
    
    return {
        "message": "弹幕已注入" if success else "注入失败",
        "data": message.model_dump()
    }


@router.post("/inject/gift")
async def inject_gift(data: GiftInject):
    """
    注入测试礼物
    
    用于测试游戏逻辑
    """
    from app.main import room_manager
    
    gift = GiftMessage(
        room_id=data.room_id,
        user_id=data.user_id,
        username=data.username,
        gift_name=data.gift_name,
        gift_count=data.gift_count,
        gift_value=data.gift_value,
        message=data.message
    )
    
    # 注入礼物
    success = await room_manager.inject_gift(data.room_id, gift)
    
    return {
        "message": "礼物已注入" if success else "注入失败",
        "data": gift.model_dump()
    }


@router.get("/realtime")
async def get_realtime_danmu(
    room_id: str,
    count: int = Query(default=50, le=200)
):
    """获取实时弹幕"""
    from app.main import room_manager
    
    messages = room_manager.get_recent_messages(room_id, count)
    
    return {
        "room_id": room_id,
        "count": len(messages),
        "messages": [m.model_dump() for m in messages]
    }
