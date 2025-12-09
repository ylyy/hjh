"""
消息处理器

负责:
1. 弹幕内容解析
2. 正则表达式匹配
3. 关键词提取
4. 命令解析
5. 投票识别
"""
import re
from typing import Optional, List, Dict, Any, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from loguru import logger

from app.models.schemas import DanmuMessage, GiftMessage, MessageType
from config import settings


@dataclass
class MatchResult:
    """匹配结果"""
    matched: bool
    rule_type: str
    rule_name: str = ""
    groups: Tuple = ()
    full_match: str = ""
    extra_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessedMessage:
    """处理后的消息"""
    original: DanmuMessage
    is_command: bool = False
    is_vote: bool = False
    is_keyword: bool = False
    command: Optional[str] = None
    command_args: List[str] = field(default_factory=list)
    vote_option: Optional[str] = None
    matched_keywords: List[str] = field(default_factory=list)
    match_results: List[MatchResult] = field(default_factory=list)


class RuleManager:
    """规则管理器"""
    
    def __init__(self):
        self._rules: Dict[str, List[Dict]] = {
            "vote": [],
            "command": [],
            "keyword": [],
            "gift_trigger": [],
            "custom": []
        }
        
        # 加载默认规则
        self._load_default_rules()
        
    def _load_default_rules(self):
        """加载默认规则"""
        # 投票规则 - 匹配 1-9 或 选1-9 或 投1-9
        self.add_rule("vote", "default_vote", settings.DEFAULT_VOTE_PATTERN)
        
        # 命令规则 - 匹配 /command 或 !command
        self.add_rule("command", "default_command", settings.DEFAULT_COMMAND_PATTERN)
        
        # 关键词规则
        for i, pattern in enumerate(settings.DEFAULT_KEYWORD_PATTERNS):
            self.add_rule("keyword", f"keyword_{i}", pattern)
            
    def add_rule(
        self, 
        rule_type: str, 
        name: str, 
        pattern: str, 
        action: str = None,
        priority: int = 0,
        config: Dict = None
    ):
        """
        添加规则
        
        Args:
            rule_type: 规则类型 (vote/command/keyword/gift_trigger/custom)
            name: 规则名称
            pattern: 正则表达式
            action: 触发动作
            priority: 优先级 (数值越大优先级越高)
            config: 额外配置
        """
        try:
            compiled = re.compile(pattern, re.IGNORECASE)
            rule = {
                "name": name,
                "pattern": pattern,
                "compiled": compiled,
                "action": action,
                "priority": priority,
                "config": config or {},
                "enabled": True
            }
            
            self._rules[rule_type].append(rule)
            # 按优先级排序
            self._rules[rule_type].sort(key=lambda x: x["priority"], reverse=True)
            
            logger.debug(f"添加规则: {rule_type}/{name}")
            
        except re.error as e:
            logger.error(f"无效正则表达式: {pattern}, 错误: {e}")
            
    def remove_rule(self, rule_type: str, name: str):
        """移除规则"""
        if rule_type in self._rules:
            self._rules[rule_type] = [
                r for r in self._rules[rule_type] if r["name"] != name
            ]
            
    def enable_rule(self, rule_type: str, name: str, enabled: bool = True):
        """启用/禁用规则"""
        for rule in self._rules.get(rule_type, []):
            if rule["name"] == name:
                rule["enabled"] = enabled
                break
                
    def match(self, rule_type: str, text: str) -> List[MatchResult]:
        """
        匹配规则
        
        Args:
            rule_type: 规则类型
            text: 待匹配文本
            
        Returns:
            匹配结果列表
        """
        results = []
        
        for rule in self._rules.get(rule_type, []):
            if not rule["enabled"]:
                continue
                
            match = rule["compiled"].search(text)
            if match:
                results.append(MatchResult(
                    matched=True,
                    rule_type=rule_type,
                    rule_name=rule["name"],
                    groups=match.groups(),
                    full_match=match.group(0),
                    extra_data={
                        "action": rule["action"],
                        "config": rule["config"]
                    }
                ))
                
        return results
    
    def get_rules(self, rule_type: str = None) -> Dict[str, List[Dict]]:
        """获取规则列表"""
        if rule_type:
            return {rule_type: self._rules.get(rule_type, [])}
        return self._rules


class MessageProcessor:
    """
    消息处理器
    
    功能:
    1. 解析弹幕消息
    2. 识别投票
    3. 解析命令
    4. 关键词匹配
    5. 礼物触发处理
    """
    
    def __init__(self):
        self.rule_manager = RuleManager()
        self._handlers: Dict[str, List[Callable]] = {}
        
    def add_rule(self, *args, **kwargs):
        """添加规则的便捷方法"""
        self.rule_manager.add_rule(*args, **kwargs)
        
    def on_match(self, rule_type: str, callback: Callable):
        """注册匹配回调"""
        if rule_type not in self._handlers:
            self._handlers[rule_type] = []
        self._handlers[rule_type].append(callback)
        
    async def process(self, message: DanmuMessage) -> ProcessedMessage:
        """
        处理弹幕消息
        
        Args:
            message: 原始弹幕消息
            
        Returns:
            处理后的消息对象
        """
        result = ProcessedMessage(original=message)
        content = message.content.strip()
        
        # 1. 检查投票
        vote_matches = self.rule_manager.match("vote", content)
        if vote_matches:
            result.is_vote = True
            # 提取投票选项
            match = vote_matches[0]
            vote_text = match.full_match
            # 提取数字
            numbers = re.findall(r'\d+', vote_text)
            if numbers:
                result.vote_option = numbers[0]
            result.match_results.extend(vote_matches)
            
        # 2. 检查命令
        command_matches = self.rule_manager.match("command", content)
        if command_matches:
            result.is_command = True
            match = command_matches[0]
            if match.groups:
                result.command = match.groups[0]
                if len(match.groups) > 1 and match.groups[1]:
                    result.command_args = match.groups[1].split()
            result.match_results.extend(command_matches)
            
        # 3. 检查关键词
        keyword_matches = self.rule_manager.match("keyword", content)
        if keyword_matches:
            result.is_keyword = True
            result.matched_keywords = [m.full_match for m in keyword_matches]
            result.match_results.extend(keyword_matches)
            
        # 4. 检查自定义规则
        custom_matches = self.rule_manager.match("custom", content)
        result.match_results.extend(custom_matches)
        
        # 5. 触发回调
        await self._trigger_callbacks(result)
        
        return result
    
    async def process_gift(self, gift: GiftMessage) -> Dict[str, Any]:
        """
        处理礼物消息
        
        Args:
            gift: 礼物消息
            
        Returns:
            处理结果
        """
        result = {
            "gift": gift,
            "triggers": [],
            "should_trigger": False
        }
        
        # 检查礼物触发规则
        if gift.message:
            matches = self.rule_manager.match("gift_trigger", gift.message)
            result["triggers"] = matches
            
        # 检查礼物价值阈值
        if gift.gift_value >= settings.GIFT_TRIGGER_THRESHOLD:
            result["should_trigger"] = True
            
        return result
    
    async def _trigger_callbacks(self, processed: ProcessedMessage):
        """触发匹配回调"""
        for match in processed.match_results:
            handlers = self._handlers.get(match.rule_type, [])
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(processed, match)
                    else:
                        handler(processed, match)
                except Exception as e:
                    logger.error(f"回调处理错误: {e}")


class VoteExtractor:
    """
    投票提取器
    
    支持多种投票格式:
    - 数字: 1, 2, 3...
    - 文字: 选1, 投2, A, B...
    - 自定义: 支持正则配置
    """
    
    def __init__(self):
        self.patterns = [
            # 纯数字
            (r'^([1-9])$', lambda m: m.group(1)),
            # 选X / 投X
            (r'^[选投]([1-9])$', lambda m: m.group(1)),
            # 字母选项
            (r'^([A-Fa-f])$', lambda m: str(ord(m.group(1).upper()) - ord('A') + 1)),
            # 选项X
            (r'^选项([1-9])$', lambda m: m.group(1)),
        ]
        self._compiled = [(re.compile(p, re.IGNORECASE), e) for p, e in self.patterns]
        
    def add_pattern(self, pattern: str, extractor: Callable = None):
        """添加投票模式"""
        if extractor is None:
            extractor = lambda m: m.group(1) if m.groups() else m.group(0)
        self._compiled.append((re.compile(pattern, re.IGNORECASE), extractor))
        
    def extract(self, text: str) -> Optional[str]:
        """
        提取投票选项
        
        Args:
            text: 弹幕文本
            
        Returns:
            投票选项 (字符串) 或 None
        """
        text = text.strip()
        
        for pattern, extractor in self._compiled:
            match = pattern.match(text)
            if match:
                try:
                    return extractor(match)
                except Exception:
                    continue
                    
        return None


class KeywordFilter:
    """
    关键词过滤器
    
    用于:
    1. 敏感词过滤
    2. 特定词汇触发
    3. 弹幕分类
    """
    
    def __init__(self):
        self._keywords: Dict[str, List[str]] = {}
        self._patterns: Dict[str, re.Pattern] = {}
        
    def add_keywords(self, category: str, keywords: List[str]):
        """添加关键词"""
        if category not in self._keywords:
            self._keywords[category] = []
        self._keywords[category].extend(keywords)
        
        # 重新编译模式
        self._compile_pattern(category)
        
    def _compile_pattern(self, category: str):
        """编译正则模式"""
        keywords = self._keywords.get(category, [])
        if keywords:
            pattern = '|'.join(re.escape(k) for k in keywords)
            self._patterns[category] = re.compile(pattern, re.IGNORECASE)
            
    def check(self, text: str, category: str = None) -> Dict[str, List[str]]:
        """
        检查文本中的关键词
        
        Args:
            text: 待检查文本
            category: 指定分类 (None表示检查所有)
            
        Returns:
            匹配结果 {分类: [匹配词]}
        """
        result = {}
        
        categories = [category] if category else self._patterns.keys()
        
        for cat in categories:
            pattern = self._patterns.get(cat)
            if pattern:
                matches = pattern.findall(text)
                if matches:
                    result[cat] = matches
                    
        return result
    
    def contains(self, text: str, category: str) -> bool:
        """检查是否包含指定分类的关键词"""
        pattern = self._patterns.get(category)
        return bool(pattern and pattern.search(text))


# 导入asyncio用于回调
import asyncio
