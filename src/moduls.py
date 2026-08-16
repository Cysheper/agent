from pydantic import BaseModel
from enum import Enum
from typing import Any

class Tools(Enum):
    Shell = "shell"
    Print = "print"


class Status(Enum):
    ToolUse: Tools 
    GetTaskList: int
    UpdateTaskList: int
    EndOfTask: int