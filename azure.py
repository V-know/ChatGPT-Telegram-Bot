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

response = openai.Completion.create(
    engine="gpt-35-turbo",
    prompt="What is the 10th fibonacci number?",
    temperature=0.8,
    max_tokens=100,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0.5,
    stop=None)


# print(response)

print(response.get('choices')[0].get('text'))