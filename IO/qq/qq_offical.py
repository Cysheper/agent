# -*- coding: utf-8 -*-
import os
import botpy
import requests
import httpx
from botpy.message import C2CMessage, GroupMessage
from dotenv import load_dotenv
load_dotenv()
from src.log import logger
import asyncio
import time

port = int(os.getenv("agent_port", 3000))
url_offical = f"http://127.0.0.1:{port}/qq_offical"

class MyClient(botpy.Client):
    async def on_ready(self):
        assert self.robot 
        logger.info(f"robot 「{self.robot.name}」 on_ready!")

    async def on_c2c_message_create(self, message: C2CMessage):
        logger.info(f"QQBOT: {message.content}")
        await self.post_message(message=message, content=message.content)

    async def on_group_at_message_create(self, message: GroupMessage):
        logger.info(f"QQBOT: {message.content}")
        await self.post_message(message=message, content=message.content)

    async def post_c2c(self, message: C2CMessage, content, count: int):
        await message._api.post_c2c_message(
            openid=message.author.user_openid, 
            msg_type=0, 
            msg_id=message.id, 
            msg_seq=str(count),
            content=content
        )
    async def post_group(self, message: GroupMessage, content, count: int):
        if not message.group_openid:
            return
        await message._api.post_group_message(
            group_openid=message.group_openid,
            msg_type=0,
            msg_id=message.id,
            msg_seq=count,
            content=content
        )

    async def post_message(self, message: GroupMessage | C2CMessage, content: str):
        # trust_env=False 禁用系统环境变量中的代理(7897)，防止代理拦截 SSE
        timeout = httpx.Timeout(60.0, connect=5.0)
        try:
            count = 1
            async with httpx.AsyncClient(timeout=timeout, trust_env=False) as client:
                async with client.stream(
                    "GET", 
                    url_offical, 
                    params={"content": content, "user_name": ""},
                    headers={"Accept": "text/event-stream"}
                ) as response:
                    # 异步按行读取 SSE 数据流，不会阻塞机器人其他任务
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        if line.startswith("data:"):
                            data = line[5:].strip()
                            # 如果后端有结束标志（如 [DONE]），可在此处判断退出
                            if data == "[DONE]" or not data:
                                continue

                            if data.startswith("[ToolUse]"):
                                data = "\n".join(data.split("\t")).strip()
                                
                            if type(message) is GroupMessage:
                                await self.post_group(message, data, count)
                            if type(message) is C2CMessage:
                                await self.post_c2c(message, data, count)
                        count += 1
        except httpx.TimeoutException as e:
            print("超时:", e)
        except Exception as e:
            print("其他异常:", type(e).__name__, e)


async def run():
    intents = botpy.Intents.all()
    client = MyClient(intents=intents)
    appid = os.getenv("AppID", None)
    secret = os.getenv("AppSecret", None)

    if not appid or not secret:
        logger.error("QQ BOT未配置appid或secret！")
        return

    async with client as c:
        await c.start(appid=appid, secret=secret)

        
if __name__ == "__main__":
    # 通过预设置的类型，设置需要监听的事件通道
    # intents = botpy.Intents.none()
    # intents.public_guild_messages=True

    # 通过kwargs，设置需要监听的事件通道
    asyncio.run(run())