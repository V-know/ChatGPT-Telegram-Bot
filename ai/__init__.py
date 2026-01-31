# -*- coding: UTF-8 -*-
"""
AI Client 模块
单例模式，复用 OpenAI/Azure 连接
"""
from db.MySqlConn import config

# 全局单例
_ai_client = None


def get_ai_client():
    """获取 AI 客户端单例"""
    global _ai_client
    if _ai_client is None:
        if config["AI"]["TYPE"] == "azure":
            from ai.azure import AzureAIClient
            _ai_client = AzureAIClient()
        else:
            from ai.openai import OpenAIClient
            _ai_client = OpenAIClient()
    return _ai_client


OPENAI_CHAT_COMPLETION_OPTIONS = {
    "temperature": 0.7,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
    "stream": True,
    "stop": None,
    "model": config["AI"]["MODEL"]
}
