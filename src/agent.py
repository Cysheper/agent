
from .LLM import LLM
from pathlib import Path
import json
from .tool import Tool
from .context import Context
from tools import *

class Agent:

    def __init__(
            self, 
            llm: LLM = LLM(), 
            context: Context = Context()
        ):
        self.LLM: LLM = llm
        self.context: Context = context
        self.system_prompt: str = self.construct_system_prompt()
        self.system_prompt_context = self.context.construct_context(
            "system", self.system_prompt
        )

    def construct_system_prompt(self) -> str:
        path: Path = Path("./prompt") 

        if not path.exists:
            return ""

        items = ["agent.md", "tools.md"]

        system_prompt: str = ""
        for i in items:
            if (path / i).exists:
                with open((path / i), 'r', encoding="UTF-8") as f:
                    system_prompt += f.read()
        system_prompt += Tool.tools_prompt
        return system_prompt

    def load_json(self, respond: str) -> dict | None:
        try:
            data: dict = json.loads(respond)
            return data
        except Exception as e:
            print("输出无法解析为json的格式！")
            if self.context.queue[-1] == \
                self \
                .context \
                .construct_context("system", "输出无法解析为json的格式！"):
                return None
            self.context.add("system", "输出无法解析为json的格式！")
            return None


    def tool_use(self, tool_name: str, args: list):
        matched = False
        for tup in Tool.tools:
            if tup[0] == tool_name:
                matched = True
                return tup[1](args)

        if not matched:
            return "Error: 没有此工具"

    def tools(self):
        print(Tool.tools)

    def matching(self, data: dict):
        try:
            end_task = False
            self.context.add("assistant", json.dumps(data, ensure_ascii=False))
            for item in data.keys():
                if item == "end_task" and data[item]:
                    end_task = True
                if item == "print":
                    for msg in data[item]:
                        print(f"Agent> {msg}")
                if item == "tool_use":
                    for name in data[item].keys():
                        args = data[item][name]["args"]
                        result = self.tool_use(tool_name=name, args=args)
                        msg = json.dumps({
                            "tool_use": {
                                "tool_name": name,
                                "args": args,
                                "result": result
                            }
                        }, ensure_ascii=False)
                        print(msg)
                        self.context.add("system", msg)
            return end_task
        
        except Exception as e:
            print(e)
            self.context.add("system", f"Error: {e}")

    def loop(self, prompt: str):
        self.context.add("user", prompt)
        
        while True:
            respond = self.LLM.get_with_context(
                self.context,
                self.system_prompt_context
            )
            if not respond: break

            data = self.load_json(respond)

            if not data: continue 

            end_task: bool | None = self.matching(data)

            if end_task: 
                # 读取task.md并完成任务
                self.context.recard()
                break




    