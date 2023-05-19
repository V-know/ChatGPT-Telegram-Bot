from config import token
import openai
from MySqlConn import config


async def ChatCompletionsAI(logged_in_user, messages) -> (str, str):
    level = logged_in_user.get("level")

    # Setup AI
    openai.api_key = config["AI"]["TOKEN"]
    openai.api_type = "azure"
    openai.api_base = "https://openaitrial0417.openai.azure.com/"
    openai.api_version = "2023-03-15-preview"

    response = await openai.ChatCompletion.acreate(
        engine="gpt-35-turbo",
        messages=messages,
        temperature=0.7,
        max_tokens=token[level],
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stream=True,
        stop=None)

    answer = ""
    async for r in response:
        delta = r.choices[0].delta
        if delta.get("content"):
            answer += delta["content"]
            yield answer, "in_progress"
        elif r.choices[0]["finish_reason"] == "stop":
            yield answer, "completed"
