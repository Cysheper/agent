from typing import cast
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionRole
from src.LLM import LLM
import os
import json

class Context:

    def __init__(self):
        self.queue: list[ChatCompletionMessageParam] = []
        self.context_length = int(os.getenv("context_length", 20))
        self.compress_length = int(os.getenv("compress_length", 10))
        self.compress_prompt = os.getenv("compress_prompt", "将以下内容压缩为简短的摘要，简要描述做了什么。")
        self.llm = LLM()

    def construct_context(
        self,
        role: ChatCompletionRole,
        message: str,
    ) -> ChatCompletionMessageParam:
        return cast(ChatCompletionMessageParam, {
            "role": role,
            "content": message,
        })

    def compress(self):
        assert(len(self.queue) >= 10)
        sub_list = str(self.queue[:self.compress_length])

        message = "【上下文已压缩】" +  str(self.llm.get(prompt=sub_list, system_prompt=self.compress_prompt))

        compress_message: ChatCompletionMessageParam = {"role": "system", "content": message}
        
        self.queue = [compress_message] + self.queue[self.compress_length:]
    

    def add(self, role: ChatCompletionRole, message: str):
        self.queue.append(self.construct_context(
            role=role, message=message
        ))

        if len(self.queue) >= self.context_length:
            self.compress()

        if len(self.queue) >= 15:
            self.clear()

    def clear(self):
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
                    pass

    def recard(self):
        with open("context.json", 'w+', encoding="UTF-8") as f:
            json.dump(self.queue, f, ensure_ascii=False, indent=2)
        

        
        