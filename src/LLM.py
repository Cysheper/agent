import requests
from openai import OpenAI
import os
from .log import logger
from openai import AsyncOpenAI

class LLM:
    def __init__(
        self, 
        model_name: str | None = os.getenv("DEEPSEEK_MODULE_NAME", None), 
        base_url: str | None = os.getenv("DEEPSEEK_API_BASE", None), 
        api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    ):
        try:
            if not model_name or not base_url:
                logger.error("Model name or Base Url not found!")
                raise Exception("Model name or Base Url not found!")
            self.name: str = model_name
            self.base_url: str = base_url
            self.api_key = api_key
            self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
            logger.info("LLM 初始化成功")
        except Exception as e:
            logger.error("LLM 初始化失败")

    async def get_with_context(self, context, system_prompt):
        try:
            respond = await self.client.chat.completions.create(
                model=self.name,
                messages=context.queue + [system_prompt],
                stream=False,
                response_format={
                    "type": "json_object"
                },
            )
            return respond.choices[0].message.content
        except Exception as e:
            logger.error(e)

    async def get(self, prompt: str, system_prompt: str = "你是一个有帮助的AI助理。"):
        try:
            respond = await self.client.chat.completions.create(
                model=self.name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                stream=False,
            )
            if respond is None:
                return "None"
            return respond.choices[0].message.content
        except Exception as e:
            logger.error(e)
            return f"Error: {e}"