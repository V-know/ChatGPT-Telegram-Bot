from config import token
from db.MySqlConn import config
from ai.openai import OpenAIClient
from ai.azure import AzureAIClient
from ai import OPENAI_CHAT_COMPLETION_OPTIONS


def init_client():
    if config["AI"]["TYPE"] == "azure":
        client = AzureAIClient()
    else:
        client = OpenAIClient()
    return client


async def ChatCompletionsAI(logged_in_user, messages) -> (str, str):
    level = logged_in_user.get("level")

    ai = init_client()
    answer = ""
    with ai.client.chat.completions.with_streaming_response.create(
            messages=messages,
            max_tokens=token[level],
            **OPENAI_CHAT_COMPLETION_OPTIONS) as response:
        for r in response.parse():
            if r.choices:
                delta = r.choices[0].delta
                if delta.content:
                    answer += delta.content
                yield answer, r.choices[0].finish_reason


async def GenerateImage(prompt):
    ai = init_client()
    image_url = ai.generate_image(prompt)
    return image_url
