from typing import cast
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionRole
from src.LLM import LLM
import os
from .log import logger
import json
from typing import Self

class Context:
    """上下文管理
    """
    def __init__(self, llm):
        try:
            self.queue: list[ChatCompletionMessageParam] = []
            self.context_length = int(os.getenv("context_length", 20))
            self.compress_length = int(os.getenv("compress_length", 10))
            self.compress_prompt = os.getenv("compress_prompt", "将以下内容压缩为简短的摘要，简要描述做了什么。")
            self.llm = llm
            logger.info("Context 初始化成功")
        except Exception as e:
            logger.error(f"Context 初始化失败: {e}")

    def construct_context(
        self,
        role: ChatCompletionRole,
        message: str,
    ) -> ChatCompletionMessageParam:
        return cast(ChatCompletionMessageParam, {
            "role": role,
            "content": message,
        })

    async def compress(self):
        try:
            sub_list = str(self.queue[:self.compress_length])

            message = "【上下文已压缩】" +  str(await self.llm.get(prompt=sub_list, system_prompt=self.compress_prompt))

            compress_message: ChatCompletionMessageParam = {"role": "system", "content": message}
            
            self.queue = [compress_message] + self.queue[self.compress_length:]
        except Exception as e:
            logger.error(f"压缩上下文时出现错误: {e}")
    

    async def add(self, role: ChatCompletionRole, message: str):
        self.queue.append(self.construct_context(
            role=role, message=message
        ))

        if len(self.queue) >= self.context_length:
           await self.compress()

        if len(self.queue) >= 15:
            self.clean()

    def clear(self):
        self.queue = []

    def clean(self):
        for i in range(max(len(self.queue) - 15, 0)):
            if self.queue[i]["role"] == "system" and "tool_use" in str(self.queue[i]["content"]): # type: ignore
                try:
                    data = json.loads(str(self.queue[i]["content"]))  # type: ignore
                    if "tool_use" not in data.keys(): continue
                    if len(data["result"]) <= 30: continue
                    self.queue[i] = {
                        "role": "system",
                        "content": f"【已压缩】Agent请求{data["tool_name"]}工具，参数{data["args"]}，已返回正确结果。"
                    }
                except:
                  logger.error("压缩tool context出现错误")

    @classmethod
    async def load_from_json(cls, id: int, llm) -> Self:
        with open(f"./context/{id}.json", "r", encoding="UTF-8") as f:
            data = json.load(f)
        assert isinstance(data, list)
        context = cls(llm)
        context.queue = data
        return context

        

        
        