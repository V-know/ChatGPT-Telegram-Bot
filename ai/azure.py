from openai import AzureOpenAI
from db.MySqlConn import config
from ai import OPENAI_CHAT_COMPLETION_OPTIONS


class AzureAIClient:
    def __init__(self):
        self.open_ai_config = {
            'api_key': config["AI"]["TOKEN"],
            'azure_endpoint': config["AI"]["BASE"],
            'api_version': config["AI"]["VERSION"]
        }

        self.client = AzureOpenAI(**self.open_ai_config)

    def get_client(self):
        return self.client

    # For testing purposes
    def chat_completions(self, messages: list):
        answer = ""
        completion = self.client.chat.completions.create(
            model=OPENAI_CHAT_COMPLETION_OPTIONS["model"],
            messages=messages
        )
        # print(completion.choices[0].message)
        return completion
