from config import token
from openai import AzureOpenAI, OpenAI
from db.MySqlConn import config

OPENAI_CHAT_COMPLETION_OPTIONS = {
    "temperature": 0.7,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
    "stream": True,
    "stop": None,
    "model": config["AI"]["MODEL"]
}


async def ChatCompletionsAI(logged_in_user, messages) -> (str, str):
    level = logged_in_user.get("level")
    open_ai_config = {'api_key': config["AI"]["TOKEN"]}

    if config["AI"]["TYPE"] == "azure":
        open_ai_config.update({
            'azure_endpoint': config["AI"]["BASE"],
            'api_version': config["AI"]["VERSION"]
        })
        client = AzureOpenAI(**open_ai_config)
    else:
        client = OpenAI(**open_ai_config)

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
