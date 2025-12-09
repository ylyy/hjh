"""
直播间管理API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Optional

from app.models.database import get_db, LiveRoom
from app.models.schemas import (
    LiveRoomCreate, LiveRoomUpdate, LiveRoomResponse, RoomStatus
)

router = APIRouter()


@router.get("/", response_model=List[LiveRoomResponse])
async def list_rooms(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """获取直播间列表"""
    query = select(LiveRoom)
    
    if status:
        query = query.filter(LiveRoom.status == status)
        
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    rooms = result.scalars().all()
    
    return rooms


@router.get("/{room_id}", response_model=LiveRoomResponse)
async def get_room(
    room_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取直播间详情"""
    query = select(LiveRoom).filter(LiveRoom.room_id == room_id)
    result = await db.execute(query)
    room = result.scalar_one_or_none()
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"直播间不存在: {room_id}"
        )
        
    return room


@router.post("/", response_model=LiveRoomResponse)
async def create_room(
    room_data: LiveRoomCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建直播间"""
    # 检查是否已存在
    query = select(LiveRoom).filter(LiveRoom.room_id == room_data.room_id)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"直播间已存在: {room_data.room_id}"
        )
        
    room = LiveRoom(
        room_id=room_data.room_id,
        name=room_data.name,
        game_type=room_data.game_type.value if room_data.game_type else None,
        game_config=room_data.game_config
    )
    
    db.add(room)
    await db.commit()
    await db.refresh(room)
    
    return room


@router.put("/{room_id}", response_model=LiveRoomResponse)
async def update_room(
    room_id: str,
    room_data: LiveRoomUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新直播间"""
    query = select(LiveRoom).filter(LiveRoom.room_id == room_id)
    result = await db.execute(query)
    room = result.scalar_one_or_none()
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"直播间不存在: {room_id}"
        )
        
    update_data = room_data.model_dump(exclude_unset=True)
    if "game_type" in update_data and update_data["game_type"]:
        update_data["game_type"] = update_data["game_type"].value
        
    for key, value in update_data.items():
        setattr(room, key, value)
        
    await db.commit()
    await db.refresh(room)
    
    return room


@router.delete("/{room_id}")
async def delete_room(
    room_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除直播间"""
    query = select(LiveRoom).filter(LiveRoom.room_id == room_id)
    result = await db.execute(query)
    room = result.scalar_one_or_none()
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"直播间不存在: {room_id}"
        )
        
    await db.delete(room)
    await db.commit()
    
    return {"message": f"直播间已删除: {room_id}"}


@router.post("/{room_id}/start")
async def start_room(
    room_id: str,
    db: AsyncSession = Depends(get_db)
):
    """启动直播间采集"""
    from app.main import room_manager
    
    query = select(LiveRoom).filter(LiveRoom.room_id == room_id)
    result = await db.execute(query)
    room = result.scalar_one_or_none()
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"直播间不存在: {room_id}"
        )
        
    # 启动采集
    success = await room_manager.start_room(room_id)
    
    if success:
        room.status = RoomStatus.RUNNING.value
        await db.commit()
        
    return {
        "message": "启动成功" if success else "启动失败",
        "room_id": room_id,
        "status": room.status
    }


@router.post("/{room_id}/stop")
async def stop_room(
    room_id: str,
    db: AsyncSession = Depends(get_db)
):
    """停止直播间采集"""
    from app.main import room_manager
    
    query = select(LiveRoom).filter(LiveRoom.room_id == room_id)
    result = await db.execute(query)
    room = result.scalar_one_or_none()
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"直播间不存在: {room_id}"
        )
        
    # 停止采集
    await room_manager.stop_room(room_id)
    
    room.status = RoomStatus.STOPPED.value
    await db.commit()
    
    return {
        "message": "已停止",
        "room_id": room_id,
        "status": room.status
    }


@router.get("/{room_id}/status")
async def get_room_status(room_id: str):
    """获取直播间运行状态"""
    from app.main import room_manager
    
    status = room_manager.get_room_status(room_id)
    
    return {
        "room_id": room_id,
        "status": status
    }
