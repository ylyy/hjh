"""
规则配置API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import re

from app.models.database import get_db, RuleConfig
from app.models.schemas import RuleConfigCreate, RuleConfigResponse

router = APIRouter()


@router.get("/", response_model=List[RuleConfigResponse])
async def list_rules(
    room_id: Optional[str] = None,
    rule_type: Optional[str] = None,
    enabled: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取规则列表"""
    query = select(RuleConfig)
    
    if room_id:
        query = query.filter(RuleConfig.room_id == room_id)
    if rule_type:
        query = query.filter(RuleConfig.rule_type == rule_type)
    if enabled is not None:
        query = query.filter(RuleConfig.enabled == enabled)
        
    query = query.order_by(RuleConfig.priority.desc())
    result = await db.execute(query)
    rules = result.scalars().all()
    
    return rules


@router.get("/{rule_id}", response_model=RuleConfigResponse)
async def get_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取规则详情"""
    query = select(RuleConfig).filter(RuleConfig.id == rule_id)
    result = await db.execute(query)
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"规则不存在: {rule_id}"
        )
        
    return rule


@router.post("/", response_model=RuleConfigResponse)
async def create_rule(
    rule_data: RuleConfigCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建规则"""
    # 验证正则表达式
    try:
        re.compile(rule_data.pattern)
    except re.error as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的正则表达式: {e}"
        )
        
    rule = RuleConfig(
        room_id=rule_data.room_id,
        rule_type=rule_data.rule_type,
        pattern=rule_data.pattern,
        action=rule_data.action,
        priority=rule_data.priority,
        enabled=rule_data.enabled,
        config=rule_data.config
    )
    
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    
    return rule


@router.put("/{rule_id}", response_model=RuleConfigResponse)
async def update_rule(
    rule_id: int,
    rule_data: RuleConfigCreate,
    db: AsyncSession = Depends(get_db)
):
    """更新规则"""
    query = select(RuleConfig).filter(RuleConfig.id == rule_id)
    result = await db.execute(query)
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"规则不存在: {rule_id}"
        )
        
    # 验证正则表达式
    try:
        re.compile(rule_data.pattern)
    except re.error as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的正则表达式: {e}"
        )
        
    for key, value in rule_data.model_dump().items():
        setattr(rule, key, value)
        
    await db.commit()
    await db.refresh(rule)
    
    return rule


@router.delete("/{rule_id}")
async def delete_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除规则"""
    query = select(RuleConfig).filter(RuleConfig.id == rule_id)
    result = await db.execute(query)
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"规则不存在: {rule_id}"
        )
        
    await db.delete(rule)
    await db.commit()
    
    return {"message": f"规则已删除: {rule_id}"}


@router.post("/{rule_id}/toggle")
async def toggle_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db)
):
    """切换规则启用状态"""
    query = select(RuleConfig).filter(RuleConfig.id == rule_id)
    result = await db.execute(query)
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"规则不存在: {rule_id}"
        )
        
    rule.enabled = not rule.enabled
    await db.commit()
    
    return {
        "message": f"规则已{'启用' if rule.enabled else '禁用'}",
        "rule_id": rule_id,
        "enabled": rule.enabled
    }


@router.post("/test")
async def test_rule(
    pattern: str,
    test_text: str
):
    """测试正则表达式"""
    try:
        compiled = re.compile(pattern, re.IGNORECASE)
        match = compiled.search(test_text)
        
        if match:
            return {
                "matched": True,
                "full_match": match.group(0),
                "groups": match.groups(),
                "start": match.start(),
                "end": match.end()
            }
        else:
            return {
                "matched": False,
                "full_match": None,
                "groups": None
            }
    except re.error as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的正则表达式: {e}"
        )


# ==================== 预设规则模板 ====================

@router.get("/templates/list")
async def list_rule_templates():
    """获取规则模板列表"""
    templates = [
        {
            "name": "投票规则 - 数字",
            "rule_type": "vote",
            "pattern": r"^[1-9]$",
            "action": "vote",
            "description": "匹配单个数字 1-9"
        },
        {
            "name": "投票规则 - 选X",
            "rule_type": "vote",
            "pattern": r"^[选投][1-9]$",
            "action": "vote",
            "description": "匹配 选1、投2 等格式"
        },
        {
            "name": "投票规则 - 字母",
            "rule_type": "vote",
            "pattern": r"^[A-Da-d]$",
            "action": "vote",
            "description": "匹配字母 A-D"
        },
        {
            "name": "命令规则 - 斜杠命令",
            "rule_type": "command",
            "pattern": r"^/(\w+)(?:\s+(.*))?$",
            "action": "command",
            "description": "匹配 /命令 参数 格式"
        },
        {
            "name": "关键词规则 - 继续",
            "rule_type": "keyword",
            "pattern": r"继续|下一个|开始",
            "action": "continue",
            "description": "匹配继续相关关键词"
        },
        {
            "name": "关键词规则 - 暂停",
            "rule_type": "keyword",
            "pattern": r"暂停|停止|等等",
            "action": "pause",
            "description": "匹配暂停相关关键词"
        },
        {
            "name": "礼物触发 - 加入剧情",
            "rule_type": "gift_trigger",
            "pattern": r".+",
            "action": "add_element",
            "description": "礼物留言触发剧情元素"
        }
    ]
    
    return {"templates": templates}


@router.post("/templates/apply")
async def apply_template(
    room_id: str,
    template_name: str,
    db: AsyncSession = Depends(get_db)
):
    """应用规则模板"""
    templates = {
        "vote_number": {
            "rule_type": "vote",
            "pattern": r"^[1-9]$",
            "action": "vote"
        },
        "vote_chinese": {
            "rule_type": "vote",
            "pattern": r"^[选投][1-9]$",
            "action": "vote"
        },
        "command": {
            "rule_type": "command",
            "pattern": r"^[/!](\w+)(?:\s+(.*))?$",
            "action": "command"
        },
        "keyword_continue": {
            "rule_type": "keyword",
            "pattern": r"继续|下一个|开始",
            "action": "continue"
        }
    }
    
    if template_name not in templates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"未知模板: {template_name}"
        )
        
    template = templates[template_name]
    
    rule = RuleConfig(
        room_id=room_id,
        rule_type=template["rule_type"],
        pattern=template["pattern"],
        action=template["action"],
        priority=0,
        enabled=True,
        config={}
    )
    
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    
    return {
        "message": f"模板已应用: {template_name}",
        "rule": rule
    }
