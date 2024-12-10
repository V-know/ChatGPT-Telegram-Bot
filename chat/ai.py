from config import token
from db.MySqlConn import config
from ai.openai import OpenAIClient
from ai.azure import AzureAIClient
from ai import OPENAI_CHAT_COMPLETION_OPTIONS


async def ChatCompletionsAI(logged_in_user, messages) -> (str, str):
    level = logged_in_user.get("level")

    if config["AI"]["TYPE"] == "azure":
        client = AzureAIClient().client
    else:
        client = OpenAIClient().client

    answer = ""
    with client.chat.completions.with_streaming_response.create(
            messages=messages,
            max_tokens=token[level],
            **OPENAI_CHAT_COMPLETION_OPTIONS) as response:
        for r in response.parse():
            if r.choices:
                delta = r.choices[0].delta
                if delta.content:
                    answer += delta.content
                yield answer, r.choices[0].finish_reason
