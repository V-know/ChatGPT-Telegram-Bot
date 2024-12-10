from config import token
from openai import OpenAI
from db.MySqlConn import config
from ai import OPENAI_CHAT_COMPLETION_OPTIONS


class OpenAIClient:
    def __init__(self):
        self.open_ai_config = {'api_key': config["AI"]["TOKEN"]}
        self.client = OpenAI(**self.open_ai_config)

    def get_client(self):
        return self.client

    def generate_image(self, model, prompt, size, quality, n):
        response = self.client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            quality=quality,
            n=n,
        )

        image_url = response.data[0].url
        return response.data, image_url

    # For testing purposes
    def chat_completions(self, messages: list):
        answer = ""
        completion = self.client.chat.completions.create(
            model=OPENAI_CHAT_COMPLETION_OPTIONS["model"],
            messages=messages
        )
        # print(completion.choices[0].message)
        return completion
