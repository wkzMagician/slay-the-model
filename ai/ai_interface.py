"""
AI decision engine interface.
Provides the interface for AI-based game decisions.
"""
from typing import Dict, List, Optional, Any
import json
import re
import logging
import asyncio
from dataclasses import dataclass, field
import json

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Normalized LLM response format."""
    thinking: Optional[str] = None
    answer: str = ""
    raw_response: Dict = field(default_factory=dict)


import re
import json
import httpx
import asyncio
import logging
from typing import Any, Dict, List, Optional, AsyncIterator
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    answer: str
    thinking: Optional[str] = None
    raw_response: Any = field(default=None, repr=False)


class LLMClient:
    """
    LLM API client，兼容 OpenAI / DeepSeek / 其他 OpenAI-compatible 端点。
    支持流式与非流式，自动提取 thinking/reasoning 内容。
    """

    def __init__(self, config: Dict[str, Any]):
        self.api_key = config.get("api_key", "")
        self.api_base = config.get("api_base", "https://api.openai.com/v1").rstrip("/")
        self.model = config.get("model", "gpt-4o")
        self.temperature = config.get("temperature", 0.7)
        # 兼容 max_token 和 max_tokens 两种写法
        self.max_tokens = config.get("max_tokens") or 16384
        self.timeout = config.get("timeout", 120)
        self.stream = config.get("stream", False)

    # ------------------------------------------------------------------
    # 公共接口
    # ------------------------------------------------------------------

    async def complete(self, messages: List[dict]) -> LLMResponse:
        """发送请求并返回 LLMResponse。自动选择流式或非流式。"""
        if self.stream:
            return await self._complete_stream(messages)
        else:
            return await self._complete_sync(messages)

    # ------------------------------------------------------------------
    # 非流式
    # ------------------------------------------------------------------

    async def _complete_sync(self, messages: List[dict]) -> LLMResponse:
        payload = self._build_payload(messages, stream=False)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(
                    f"{self.api_base}/chat/completions",
                    headers=self._headers(),
                    json=payload,
                )
                resp.raise_for_status()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error: {e.response.status_code} {e.response.text}")
                raise
            except httpx.TimeoutException:
                logger.error("Request timed out (sync mode)")
                raise

        return self._parse_sync_response(resp.json())

    def _parse_sync_response(self, data: dict) -> LLMResponse:
        choice = data.get("choices", [{}])[0]
        message = choice.get("message", {})
        content = message.get("content") or ""
        # DeepSeek R1 非流式：thinking 在 reasoning_content 字段
        reasoning = message.get("reasoning_content")

        if reasoning:
            return LLMResponse(thinking=reasoning.strip(), answer=content.strip(), raw_response=data)

        # 部分模型把 thinking 放在 <think>...</think> 标签里
        if "<think" in content:
            thinking, answer = self._extract_think_tags(content)
            return LLMResponse(thinking=thinking, answer=answer, raw_response=data)

        return LLMResponse(answer=content.strip(), raw_response=data)

    # ------------------------------------------------------------------
    # 流式
    # ------------------------------------------------------------------

    async def _complete_stream(self, messages: List[dict]) -> LLMResponse:
        payload = self._build_payload(messages, stream=True)

        thinking_chunks: List[str] = []
        answer_chunks: List[str] = []
        raw_chunks: List[dict] = []

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                async with client.stream(
                    "POST",
                    f"{self.api_base}/chat/completions",
                    headers=self._headers(),
                    json=payload,
                ) as resp:
                    resp.raise_for_status()
                    async for line in resp.aiter_lines():
                        chunk = self._parse_sse_line(line)
                        if chunk is None:
                            continue
                        raw_chunks.append(chunk)

                        delta = self._extract_delta(chunk)
                        # DeepSeek R1 流式：reasoning_content delta
                        rc = delta.get("reasoning_content")
                        if rc:
                            thinking_chunks.append(rc)
                        # 普通 content delta
                        c = delta.get("content")
                        if c:
                            answer_chunks.append(c)

            except httpx.TimeoutException:
                logger.error("Request timed out (stream mode)")
                raise
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error: {e.response.status_code} {e.response.text}")
                raise

        thinking_text = "".join(thinking_chunks).strip() or None
        answer_text = "".join(answer_chunks).strip()

        # 如果 answer 里有 <think> 标签（某些模型流式也会这样输出）
        if not thinking_text and "<think" in answer_text:
            thinking_text, answer_text = self._extract_think_tags(answer_text)

        return LLMResponse(
            thinking=thinking_text,
            answer=answer_text,
            raw_response=raw_chunks,
        )

    # ------------------------------------------------------------------
    # 工具方法
    # ------------------------------------------------------------------

    def _build_payload(self, messages: List[dict], stream: bool) -> dict:
        return {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": stream,
        }

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",  # 流式和非流式都带上没有副作用
        }

    @staticmethod
    def _parse_sse_line(line: str) -> Optional[dict]:
        """解析 SSE 行，返回 JSON dict 或 None（忽略心跳/结束标记）。"""
        line = line.strip()
        if not line or line == "data: [DONE]":
            return None
        if line.startswith("data:"):
            line = line[5:].strip()
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            logger.debug(f"Non-JSON SSE line (ignored): {line!r}")
            return None

    @staticmethod
    def _extract_delta(chunk: dict) -> dict:
        """从 chunk 中提取 delta 字段，兼容不同结构。"""
        choices = chunk.get("choices", [])
        if not choices:
            return {}
        return choices[0].get("delta", {})

    @staticmethod
    def _extract_think_tags(content: str):
        """
        从 content 中提取 <think>...</think> 标签内容。
        返回 (thinking: str | None, answer: str)
        """
        match = re.search(r"<think[^>]*>(.*?)</think>", content, re.DOTALL)
        if match:
            thinking = match.group(1).strip()
            answer = re.sub(r"<think[^>]*>.*?</think>", "", content, flags=re.DOTALL).strip()
            return thinking, answer
        # 标签未闭合时（流被截断），尽量提取已有思考内容
        match_open = re.search(r"<think[^>]*>(.*)", content, re.DOTALL)
        if match_open:
            thinking = match_open.group(1).strip()
            answer = content[: content.index("<think")].strip()
            return thinking, answer
        return None, content


class AIDecisionEngine:
    """
    Base interface for AI decision making.
    
    This class provides the interface for AI systems to make game decisions.
    It can be extended with specific implementations using LLMs, rule-based systems,
    or other AI approaches.
    """
    
    def __init__(self, debug: bool = False):
        """
        Initialize AI decision engine.
        
        Args:
            debug: Whether to enable debug logging
        """
        self.debug = debug
    
    def make_map_decision(self, map_context: Dict) -> int:
        """
        Make a decision about which map node to move to.
        
        Args:
            map_context: Dict containing map information with the following structure:
                - current_floor: Current floor number
                - current_position: Current position on current floor
                - map_ascii: ASCII representation of the map
                - map_json: Structured JSON data
                - available_moves: List of available moves with metadata
                  Each move has: index, floor, position, room_type, risk_level, reward_level
        
        Returns:
            int: The index of the chosen move in the available_moves list (0-based)
        
        Raises:
            ValueError: If no available moves or invalid index returned
        """
        available_moves = map_context.get("available_moves", [])
        
        if not available_moves:
            raise ValueError("No available moves to choose from")
        
        if self.debug:
            self._log_map_context(map_context)
        
        # Default implementation: choose first available move
        # This should be overridden by specific AI implementations
        choice_index = 0
        
        if self.debug:
            print(f"[AI Debug] Choosing move at index {choice_index}:")
            print(f"  Floor: {available_moves[choice_index]['floor']}")
            print(f"  Position: {available_moves[choice_index]['position']}")
            print(f"  Room Type: {available_moves[choice_index]['room_type']}")
            print(f"  Risk Level: {available_moves[choice_index]['risk_level']}")
            print(f"  Reward Level: {available_moves[choice_index]['reward_level']}")
        
        return choice_index
    
    def _log_map_context(self, map_context: Dict):
        """Log map context for debugging"""
        print("[AI Debug] Map Context:")
        print(f"  Current Floor: {map_context['current_floor']}")
        print(f"  Current Position: {map_context['current_position']}")
        print(f"  Available Moves: {len(map_context['available_moves'])}")
        print("\n[AI Debug] ASCII Map:")
        print(map_context['map_ascii'])
        print("\n[AI Debug] Available Moves:")
        for move in map_context['available_moves']:
            print(f"  [{move['index']}] Floor {move['floor']}, Pos {move['position']}: "
                  f"{move['room_type']} (Risk: {move['risk_level']}, Reward: {move['reward_level']})")


class MockAIDecisionEngine(AIDecisionEngine):
    """
    Mock AI decision engine for testing.
    
    This implementation uses simple heuristics for decision making,
    useful for testing without requiring a full LLM integration.
    """
    
    def __init__(self, strategy: str = "first", debug: bool = False):
        """
        Initialize mock AI engine.
        
        Args:
            strategy: Decision strategy ('first', 'last', 'random', 'least_risk', 'highest_reward')
            debug: Whether to enable debug logging
        """
        super().__init__(debug)
        self.strategy = strategy
        import random
        self.random = random.Random()
    
    def make_map_decision(self, map_context: Dict) -> int:
        """
        Make a decision using the configured strategy.
        
        Args:
            map_context: Dict containing map information
            
        Returns:
            int: The index of the chosen move
        """
        available_moves = map_context.get("available_moves", [])
        
        if not available_moves:
            raise ValueError("No available moves to choose from")
        
        if self.debug:
            self._log_map_context(map_context)
        
        if self.strategy == "first":
            choice_index = 0
        
        elif self.strategy == "last":
            choice_index = len(available_moves) - 1
        
        elif self.strategy == "random":
            choice_index = self.random.randint(0, len(available_moves) - 1)
        
        elif self.strategy == "least_risk":
            # Choose move with lowest risk level
            risk_priority = {
                "NONE": 0,
                "LOW": 1,
                "MEDIUM": 2,
                "HIGH": 3,
                "VERY_HIGH": 4,
                "RANDOM": 5
            }
            choice_index = min(
                range(len(available_moves)),
                key=lambda i: risk_priority.get(available_moves[i]['risk_level'], 999)
            )
        
        elif self.strategy == "highest_reward":
            # Choose move with highest reward level
            reward_priority = {
                "NONE": 0,
                "HEAL": 1,
                "SHOP": 2,
                "MEDIUM": 3,
                "HIGH": 4,
                "VERY_HIGH": 5,
                "RANDOM": 1  # Random rewards average to medium
            }
            choice_index = max(
                range(len(available_moves)),
                key=lambda i: reward_priority.get(available_moves[i]['reward_level'], 0)
            )
        
        else:
            # Default to first
            choice_index = 0
        
        if self.debug:
            print(f"[AI Debug] Strategy: {self.strategy}")
            print(f"[AI Debug] Choosing move at index {choice_index}:")
            print(f"  Floor: {available_moves[choice_index]['floor']}")
            print(f"  Position: {available_moves[choice_index]['position']}")
            print(f"  Room Type: {available_moves[choice_index]['room_type']}")
            print(f"  Risk Level: {available_moves[choice_index]['risk_level']}")
            print(f"  Reward Level: {available_moves[choice_index]['reward_level']}")
        
        return choice_index

class LLMDecisionEngine(AIDecisionEngine):
    """LLM-based decision engine."""
    
    def __init__(self, config: Dict[str, Any], debug: bool = False):
        super().__init__(debug)
        self.client = LLMClient(config)
        self._last_answer: Optional[str] = None  # Store last answer for display
    
    def make_decision(
        self,
        title: str,
        options: List[str],
        context: Optional[Dict[str, Any]] = None,
        max_select: int = 1,
    ) -> List[int]:
        """Sync interface, returns 0-indexed list."""
        result = self.make_decision_with_thinking(title, options, context, max_select)
        return result[0]
    
    def make_decision_with_thinking(
        self,
        title: str,
        options: List[str],
        context: Optional[Dict[str, Any]] = None,
        max_select: int = 1,
    ) -> tuple:
        """Sync interface that returns (indices, thinking)."""
        return asyncio.run(self._make_decision_async(title, options, context, max_select))
    
    async def _make_decision_async(
        self,
        title: str,
        options: List[str],
        context: Optional[Dict[str, Any]],
        max_select: int,
    ) -> tuple:
        """Async decision implementation. Returns (indices, thinking)."""
        messages = self._build_messages(title, options, context, max_select)
        
        try:
            response = await self.client.complete(messages)
            indices = self._parse_indices(response.answer, len(options))
            thinking = response.thinking
            
            # Store last answer for display purposes
            self._last_answer = response.answer
            
            if self.debug:
                logger.info(f"[LLM] Thinking: {response.thinking}")
                logger.info(f"[LLM] Answer: {response.answer}")
                logger.info(f"[LLM] Parsed indices: {indices}")
            
            indices = indices[:max_select] if max_select > 0 else indices
            return indices, thinking
        except Exception as e:
            logger.error(f"LLM decision error: {e}")
            self._last_answer = None
            return [], None
    
    def _build_messages(
        self,
        title: str,
        options: List[str],
        context: Optional[Dict[str, Any]],
        max_select: int = 1,
    ) -> List[dict]:
        """Build messages for LLM."""
        from localization import t
        
        # Build system prompt with selection constraint
        base_system_prompt = t("ai.decision_system_prompt")
        
        # Add selection constraint based on max_select
        if max_select == 1:
            selection_constraint = t("ai.selection_single")
        else:
            selection_constraint = t("ai.selection_multiple").format(max_select=max_select)
        
        system_prompt = f"{base_system_prompt}\n\n{selection_constraint}"
        
        # Format options
        options_text = "\n".join(f"{i+1}. {opt}" for i, opt in enumerate(options))
        
        # Format context
        context_text = self._format_context(context) if context else "N/A"
        
        # Build user content
        user_content = f"## Decision Scenario\n{title}\n\n"
        user_content += f"## Game State\n{context_text}\n\n"
        user_content += f"## Options ({len(options)} total)\n{options_text}\n\n"
        
        # Add selection instruction
        if max_select == 1:
            user_content += "Select ONE option (output just the number, e.g., '2'):"
        else:
            user_content += f"Select up to {max_select} options (output numbers separated by commas, e.g., '1, 3'):"
        
        # Print full prompt for debugging
        if self.debug:
            print("\n" + "=" * 60)
            print("[AI PROMPT] System Message:")
            print("-" * 60)
            print(system_prompt)
            print("-" * 60)
            print("[AI PROMPT] User Message:")
            print("-" * 60)
            print(user_content)
            print("=" * 60 + "\n")
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context dict to readable text.
        
        If context contains 'game_state' key with a string value (from AIContextBuilder),
        return that string directly as it's already formatted Markdown.
        """
        # Check if we have a pre-formatted game_state string from AIContextBuilder
        if 'game_state' in context and isinstance(context['game_state'], str):
            return context['game_state']
        
        # Otherwise, format as key-value pairs
        lines = []
        for key, value in context.items():
            if isinstance(value, dict):
                lines.append(f"- {key}: {json.dumps(value, ensure_ascii=False)}")
            else:
                lines.append(f"- {key}: {value}")
        return "\n".join(lines)
    
    def _parse_indices(self, answer: str, max_index: int) -> List[int]:
        """Parse '1, 3, 5' format to 0-indexed list.
        
        Tries multiple strategies to extract the intended choice numbers:
        1. Direct answer at start (e.g., "1", "2, 3")
        2. Explicit choice patterns (e.g., "I choose 1", "option 2")
        3. Fallback to all valid numbers
        """
        answer = answer.strip()
        
        # Strategy 1: Direct answer at start
        # Pattern: numbers with optional commas at the beginning
        direct_pattern = r'^[\s]*(\d+(?:\s*,\s*\d+)*)'
        match = re.match(direct_pattern, answer)
        
        if match:
            # Found direct answer pattern at start - use only these numbers
            numbers = re.findall(r'\d+', match.group(1))
        else:
            # Strategy 2: Look for explicit choice patterns
            # Common patterns: "choose X", "select X", "option X", "pick X"
            choice_patterns = [
                r'(?:choose|select|pick|go\s+with|my\s+choice\s+is)\s*[#:]?\s*(\d+(?:\s*,\s*\d+)*)',
                r'option\s*[#:]?\s*(\d+(?:\s*,\s*\d+)*)',
                r'(?:answer|selection|result)\s*(?:is)?\s*[#:]?\s*(\d+(?:\s*,\s*\d+)*)',
            ]
            
            found_choice = False
            for pattern in choice_patterns:
                match = re.search(pattern, answer, re.IGNORECASE)
                if match:
                    numbers = re.findall(r'\d+', match.group(1))
                    found_choice = True
                    break
            
            if not found_choice:
                # Strategy 3: Fallback to all numbers (but only keep valid indices)
                numbers = re.findall(r'\d+', answer)
        
        # Convert to 0-indexed and filter valid
        indices = []
        for n in numbers:
            idx = int(n) - 1  # Convert 1-indexed to 0-indexed
            if 0 <= idx < max_index and idx not in indices:
                indices.append(idx)
        
        # If no valid indices found, return empty (don't default to first)
        return indices
