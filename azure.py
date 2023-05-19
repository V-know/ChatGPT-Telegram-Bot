# Note: The openai-python library support for Azure OpenAI is in preview.
import os
import openai
import yaml

with open("config.yaml") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
openai.api_type = "azure"
openai.api_base = "https://openaitrial0417.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
openai.api_key = config["AI"]["TOKEN"]

response = openai.ChatCompletion.create(
    engine="gpt-35-turbo",
    messages=[{"role": "system", "content": "You are an AI assistant that helps people find information."},
              {"role": "user", "content": "你好！"}],
    temperature=0.5,
    max_tokens=800,
    top_p=0.95,
    frequency_penalty=0,
    stream=True,
    presence_penalty=0,
    stop=None)

# print(response.get('choices')[0].get('message').get('content'))
# print(response)
i = 0
for r in response:
    i += 1
    print(i)
    print(r)
