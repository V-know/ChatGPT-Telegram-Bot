# -*- coding: UTF-8 -*-
"""
Token 计算工具模块
使用 tiktoken 精确计算 OpenAI API 的 token 数量
"""
import tiktoken
import logging

logger = logging.getLogger(__name__)

# 缓存 encoding 实例
_encoding_cache = {}


def get_encoding(model: str = "gpt-3.5-turbo"):
    """获取指定模型的 encoding（带缓存）"""
    if model not in _encoding_cache:
        try:
            _encoding_cache[model] = tiktoken.encoding_for_model(model)
        except KeyError:
            # 未知模型，使用 cl100k_base（GPT-4/3.5 系列通用）
            logger.warning(f"Unknown model {model}, using cl100k_base encoding")
            _encoding_cache[model] = tiktoken.get_encoding("cl100k_base")
    return _encoding_cache[model]


def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """
    计算文本的 token 数量
    
    Args:
        text: 要计算的文本
        model: 模型名称（用于选择正确的 tokenizer）
        
    Returns:
        token 数量
    """
    if not text:
        return 0
    
    try:
        encoding = get_encoding(model)
        return len(encoding.encode(text))
    except Exception as e:
        logger.error(f"Token counting failed: {e}, falling back to estimate")
        # 降级: 粗略估算 (中文约 2 字符/token, 英文约 4 字符/token)
        return len(text) // 3


def count_messages_tokens(messages: list, model: str = "gpt-3.5-turbo") -> int:
    """
    计算消息列表的总 token 数量
    
    OpenAI 的消息格式有额外开销:
    - 每条消息有 ~4 tokens 的结构开销
    - 整个请求有 ~3 tokens 的基础开销
    
    Args:
        messages: OpenAI 消息格式 [{"role": "...", "content": "..."}]
        model: 模型名称
        
    Returns:
        总 token 数量
    """
    encoding = get_encoding(model)
    
    # 消息结构开销
    tokens_per_message = 4  # <|start|>role<|separator|>content<|end|>
    tokens_base = 3  # 请求基础开销
    
    total = tokens_base
    for message in messages:
        total += tokens_per_message
        for key, value in message.items():
            if value:
                total += len(encoding.encode(str(value)))
    
    return total
