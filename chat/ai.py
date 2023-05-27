from config import token
import openai
from MySqlConn import config


async def ChatCompletionsAI(logged_in_user, messages) -> (str, str):
    level = logged_in_user.get("level")

    # Setup AI
    openai.api_key = config["AI"]["TOKEN"]
    openai.api_type = config["AI"]["TYPE"]
    openai.api_base = config["AI"]["BASE"]
    openai.api_version = config["AI"]["VERSION"]

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
