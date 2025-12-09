"""
AI服务模块

提供:
1. 文本生成 (故事、对话等)
2. 内容分析
3. 多模型支持 (OpenAI, 文心一言等)
"""
from typing import Optional, Dict, Any, List, AsyncGenerator
from abc import ABC, abstractmethod
import asyncio
import httpx
from loguru import logger

from config import settings


class BaseAIProvider(ABC):
    """AI提供者基类"""
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """生成文本"""
        pass
    
    @abstractmethod
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: str = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式生成文本"""
        pass


class OpenAIProvider(BaseAIProvider):
    """OpenAI提供者"""
    
    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.base_url = base_url or settings.OPENAI_BASE_URL or "https://api.openai.com/v1"
        self.model = model or settings.OPENAI_MODEL
        
    async def generate(
        self,
        prompt: str,
        system_prompt: str = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """生成文本"""
        if not self.api_key:
            logger.warning("OpenAI API Key未配置")
            return self._mock_generate(prompt)
            
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "max_tokens": max_tokens,
                        "temperature": temperature
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except Exception as e:
                logger.error(f"OpenAI API调用失败: {e}")
                return self._mock_generate(prompt)
    
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: str = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式生成"""
        if not self.api_key:
            yield self._mock_generate(prompt)
            return
            
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        async with httpx.AsyncClient() as client:
            try:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                        "stream": True
                    },
                    timeout=60.0
                ) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            try:
                                import json
                                chunk = json.loads(data)
                                content = chunk["choices"][0]["delta"].get("content", "")
                                if content:
                                    yield content
                            except Exception:
                                continue
            except Exception as e:
                logger.error(f"OpenAI流式API调用失败: {e}")
                yield self._mock_generate(prompt)
    
    def _mock_generate(self, prompt: str) -> str:
        """模拟生成 (用于测试或API不可用时)"""
        return f"[模拟AI响应] 收到提示: {prompt[:50]}..."


class AIService:
    """
    AI服务
    
    提供统一的AI调用接口，支持多种AI提供者
    """
    
    def __init__(self, provider: BaseAIProvider = None):
        self.provider = provider or OpenAIProvider()
        self._cache: Dict[str, str] = {}
        
    def set_provider(self, provider: BaseAIProvider):
        """设置AI提供者"""
        self.provider = provider
        
    async def generate_text(
        self,
        prompt: str,
        system_prompt: str = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        use_cache: bool = False,
        **kwargs
    ) -> str:
        """
        生成文本
        
        Args:
            prompt: 用户提示
            system_prompt: 系统提示
            max_tokens: 最大token数
            temperature: 温度参数
            use_cache: 是否使用缓存
            
        Returns:
            生成的文本
        """
        # 检查缓存
        cache_key = f"{prompt}:{system_prompt}:{max_tokens}:{temperature}"
        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]
            
        result = await self.provider.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
        
        if use_cache:
            self._cache[cache_key] = result
            
        return result
    
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: str = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式生成文本"""
        async for chunk in self.provider.generate_stream(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        ):
            yield chunk
    
    # ==================== 专用生成方法 ====================
    
    async def generate_story(
        self,
        context: str,
        direction: str = None,
        style: str = "悬疑",
        length: str = "medium"
    ) -> str:
        """
        生成故事
        
        Args:
            context: 故事上下文
            direction: 发展方向 (由观众选择)
            style: 故事风格
            length: 长度 (short/medium/long)
        """
        length_tokens = {"short": 200, "medium": 400, "long": 800}
        
        system_prompt = f"""你是一个{style}小说作家。
请继续写作故事，保持紧凑有趣的节奏。
每段结尾提供2-3个选项让观众选择接下来的发展方向。
用【选项1】【选项2】【选项3】的格式标注选项。
"""
        
        prompt = f"故事背景和之前的内容:\n{context}\n\n"
        if direction:
            prompt += f"观众选择的方向: {direction}\n\n"
        prompt += "请继续写下一段故事:"
        
        return await self.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=length_tokens.get(length, 400),
            temperature=0.8
        )
    
    async def generate_puzzle(
        self,
        theme: str,
        difficulty: str = "medium",
        context: str = None
    ) -> Dict[str, Any]:
        """
        生成谜题
        
        Args:
            theme: 谜题主题
            difficulty: 难度
            context: 上下文
            
        Returns:
            谜题数据
        """
        difficulty_map = {"easy": "简单", "medium": "中等", "hard": "困难"}
        
        system_prompt = f"""你是一个谜题设计师。
请设计一个{difficulty_map.get(difficulty, '中等')}难度的{theme}谜题。
返回JSON格式:
{{
    "question": "谜题描述",
    "options": ["选项1", "选项2", "选项3", "选项4"],
    "answer": 0,  // 正确答案索引
    "hint": "提示",
    "explanation": "解析"
}}
"""
        
        prompt = "请设计一个谜题"
        if context:
            prompt += f"，与以下内容相关:\n{context}"
            
        result = await self.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=500,
            temperature=0.7
        )
        
        # 尝试解析JSON
        try:
            import json
            # 提取JSON部分
            import re
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.warning(f"解析谜题JSON失败: {e}")
            
        # 返回默认格式
        return {
            "question": result,
            "options": ["选项1", "选项2", "选项3", "选项4"],
            "answer": 0,
            "hint": "无提示",
            "explanation": "无解析"
        }
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """分析文本情感"""
        system_prompt = """分析以下文本的情感，返回JSON:
{
    "sentiment": "positive/negative/neutral",
    "score": 0.0-1.0,
    "keywords": ["关键词1", "关键词2"]
}"""
        
        result = await self.generate_text(
            prompt=text,
            system_prompt=system_prompt,
            max_tokens=100,
            temperature=0.3
        )
        
        try:
            import json
            import re
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass
            
        return {"sentiment": "neutral", "score": 0.5, "keywords": []}
    
    def clear_cache(self):
        """清除缓存"""
        self._cache.clear()
