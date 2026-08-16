import requests
from openai import OpenAI
import os

class LLM:
    def __init__(
        self, 
        model_name: str | None = os.getenv("model_name", None), 
        base_url: str | None = os.getenv("base_url", None), 
        api_key: str = os.getenv("api_key", "")
    ):
        if not model_name or not base_url:
            print(model_name, base_url)
            raise Exception("Model name or Base Url not found!")
        self.name: str = model_name
        self.base_url: str = base_url
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def get_with_context(self, context, system_prompt):
        try:
            return self.client.chat.completions.create(
                model=self.name,
                messages=context.queue + [system_prompt],
                stream=False,
                response_format={
                    "type": "json_object"
                },
            ).choices[0].message.content
        except Exception as e:
            print(f"Error: {e}")

    def get(self, prompt: str, system_prompt: str):
        try:
            respond = self.client.chat.completions.create(
                model=self.name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                stream=False,
            ).choices[0].message.content

            return respond
        except Exception as e:
            print(f"Error: {e}")