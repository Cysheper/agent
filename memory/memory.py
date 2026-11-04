
import sqlite3
from subprocess import run


class Memory:
    def __init__(self):
        self.connect = sqlite3.connect('')

    @classmethod
    def get(cls, keyword: str) -> str:
        # TODO: Connect the Memory System 
        return run(["./mem", "get", keyword], capture_output=True, text=True).stdout

    @classmethod
    def add(cls, content: str):
        run(["./mem", "add", content])