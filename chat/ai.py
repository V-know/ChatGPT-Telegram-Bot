from config import token
from ai import get_ai_client, OPENAI_CHAT_COMPLETION_OPTIONS


async def ChatCompletionsAI(logged_in_user, messages) -> (str, str):
    level = logged_in_user.get("level")

    ai = get_ai_client()
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
    ai = get_ai_client()
    image_url = ai.generate_image(prompt)
    return image_url
