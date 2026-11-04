import sqlite3
from .log import logger

class DB:
    def __init__(self):
        try:
            self.connect = sqlite3.connect('./database/agent.db')
            self.cursor = self.connect.cursor()
            logger.info("DB 初始化成功")
        except Exception as e:
            logger.error(f"DB 初始化失败: {e}")

    async def add(self, role: str, message: str):
        self.cursor.execute(f'''
            INSERT INTO "AgentData" (created_time, role, content)
            VALUES (datetime('now', 'localtime'), ?, ?);
        ''', (role, message))
        self.connect.commit()