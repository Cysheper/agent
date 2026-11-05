from .LLM import LLM
from pathlib import Path
import json
from .tool import Tool
from .context import Context
from tools import *
from .log import logger
from .database import DB
import inspect
from .channle import Output
from .module import *

def construct_system_prompt(path: Path) -> str:
    """ 构造系统提示词
        在./prompt 下找fish.md agent.md tools.md文件
    """
    if not path.exists():
        logger.error(f"不存在的路径或文件: {str(path)}")
        raise Exception(f"不存在的路径或文件: {str(path)}")

    # 暂时硬编码文件名
    items = ["agent.md", "tools.md", "travel.md"]

    system_prompt: str = ""
    for i in items:
        if (path / i).exists:
            with open((path / i), 'r', encoding="UTF-8") as f:
                system_prompt += f.read()
    system_prompt += Tool.tools_prompt
    return system_prompt
 
class Agent:
    def __init__(
        self, 
        llm: LLM = LLM(), 
        system_prompt: str = construct_system_prompt(Path("./prompt")),
        db: DB = DB()
    ):
        try:
            self.LLM: LLM = llm
            self.context: Context = Context(llm)
            self.path: Path = Path("./prompt")
            self.system_prompt: str = system_prompt
            self.system_prompt_context = self.context.construct_context(
                "system", self.system_prompt
            )
            self.db: DB = db
            self.is_stop: bool = False
            self.is_running: bool = False
            self.output = Output()
            if len(self.tools()) == 0: 
                logger.error("Tool 列表获取失败")
                raise Exception("Tool 列表获取失败")
            logger.info("Agent 初始化成功")
        except Exception as e:
            logger.error(f"Agent 初始化失败: {e}")

    async def load_json(self, respond: str) -> dict | None:
        """ 解析输出为json格式
        """
        try:
            data: dict = json.loads(respond)
            return data
        except Exception as e:
            logger.error("输出无法解析为json的格式！")
            print(respond)
            if self.context.queue[-1] == \
                self \
                .context \
                .construct_context("system", "输出无法解析为json的格式！"):
                return None
            await self.context.add("system", "输出无法解析为json的格式！")
            return None

    async def tool_use(self, tool_name: str, args: dict):
        """ 调用工具
        """
        matched = False
        # tup: (name, tool_function)
        for tup in Tool.tools:
            if tup[0] == tool_name:
                matched = True
                try:
                    # 判断是否可await
                    if inspect.isawaitable(tup[1]):
                        answer = await tup[1](**args)
                    else:
                        answer = tup[1](**args)
                    return answer
                except Exception as e:
                    err = f"函数内部错误或者参数错误: 函数: {tool_name}, 参数: {args}, 报错: {e}"
                    logger.error(err)
                    return err

        if not matched:
            logger.error(f"不存在的工具: {tool_name}")
            return "Error: 没有此工具"

    def tools(self):
        return Tool.tools

    def clear(self):
        self.context.clear()

    async def matching(self, data: dict) -> tuple[bool, list]:
        print(data)
        end_task, message_list = False, []
        try:
            await self.context.add("assistant", json.dumps(data, ensure_ascii=False))
            for item in data.keys():
                if item == "end_task" and data[item]:
                    end_task = True
                if item == "print":
                    for msg in data[item]:
                        message_list.append(
                            Message(
                                input=Channle.Console, 
                                role=Role.Agent,
                                content=msg,
                                output=Channle.Console
                            )
                        )
                if item == "tool_use":
                    for name in data[item].keys():
                        args = data[item][name]
                        result = await self.tool_use(tool_name=name, args=args)
                        msg = ToolUse(
                            tool_name=name,
                            args=args,
                            result=result
                        )
                        message_list.append(
                            Message(
                                input=Channle.Console,
                                role=Role.Tool,
                                content=msg,
                                output=Channle.Console
                            )
                        )
                        print(msg)
                        await self.context.add("system", msg.model_dump_json())
            return end_task, message_list
        
        except Exception as e:
            logger.error(str(e))
            await self.context.add("system", f"Error: {e}")
            return False, message_list
 
    async def loop(self, message: Message):
        self.is_running = True
        assert type(message.content) is User 
        await self.db.add("user", message.content.content)
        await self.context.add("user", message.content.content)
        while True:
            respond = await self.LLM.get_with_context(
                self.context,
                self.system_prompt_context
            )
            if not respond: break

            data = await self.load_json(respond)
            if not data: continue
            
            end_task, message_list = await self.matching(data)

            for message in message_list:
                yield f"data: {message.construct()}\n\n"

            if end_task or self.is_stop: 
                self.is_stop = False
                break
        self.is_running = False

    def stop(self):
        self.is_stop = True




    