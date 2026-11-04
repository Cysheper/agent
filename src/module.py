from pydantic import BaseModel
from enum import Enum
from typing import Any
from typing import Type, Union

class Channle(Enum):
    Console = 1
    WebUI = 2
    QQ = 3

class Role(Enum):
    Agent = 1
    User = 2
    System = 3
    Tool = 4

class User:
    def __init__(self, content: str):
        self.content = content


from typing import Literal
StatusCode = Literal["ok", "error"]

class Status(BaseModel):
    code: StatusCode
    message: str
    
class ToolUse(BaseModel):
    tool_name: str
    args: dict
    result: Any


content_type = Union[str, ToolUse, User]

class Message:
    def __init__(self, input: Channle, role: Role, content: content_type, output):
        self.input: Channle = input
        self.role: Role = role
        self.content: content_type = content
        self.output: Channle = output

        data = ""
        match self.role:
            case Role.User:
                data = "[InputChannle] "
                match self.input:
                    case Channle.Console:
                        data += "Console"
                    case Channle.WebUI:
                        data += "WebUI"
                    case Channle.QQ:
                        data += "QQ"
                assert type(self.content) is User
                self.content.content = data + self.content.content


    def construct(self) -> str:
        data = ""
        match self.role:
            case Role.User:
                data += "[InputChannle] "
                match self.input:
                    case Channle.Console:
                        data += "Console"
                    case Channle.WebUI:
                        data += "WebUI"
                    case Channle.QQ:
                        data += "QQ"
                assert type(self.content) is User
                data += self.content.content
            case Role.Agent:
                assert type(self.content) is str
                data += self.content
            case Role.Tool:
                assert type(self.content) is ToolUse
                data += f"[ToolUse]\ttool_name={self.content.tool_name}\targs={self.content.args}\treturns={self.content.result}"

        return data





        




