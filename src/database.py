import os
import sqlite3
from .log import logger

class DB:
    def __init__(self):
        try:
            # 首次运行时 ./database 目录可能不存在（git 不跟踪空目录）
            os.makedirs('./database', exist_ok=True)
            self.connect = sqlite3.connect('./database/agent.db')
            self.cursor = self.connect.cursor()
            # 表不存在则自动创建（与既有库结构一致）
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS "AgentData" (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    created_time TEXT NOT NULL,
                    "role" TEXT NOT NULL,
                    content TEXT NOT NULL
                );
            ''')
            self.connect.commit()
            logger.info("DB 初始化成功")
        except Exception as e:
            logger.error(f"DB 初始化失败: {e}")

    async def add(self, role: str, message: str):
        self.cursor.execute(f'''
            INSERT INTO "AgentData" (created_time, role, content)
            VALUES (datetime('now', 'localtime'), ?, ?);
        ''', (role, message))
        self.connect.commit()
