from dotenv import load_dotenv
load_dotenv()
from src.agent import Agent
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import uvicorn
import os
from src.module import *
from fastapi.responses import StreamingResponse

# @asynccontextmanager
# async def lifespan(app):
#     # 启动时创建 botpy 后台任务
#     qq_task = asyncio.create_task(qq_offical.run())
#     yield
#     # 关闭时取消
#     qq_task.cancel()

app = FastAPI()# lifespan=lifespan
agent = Agent()

@app.get("/qq_offical")
async def qq_offical_func(user_name: str, content: str):
    async def event_stream():
        yield ": Connected Successfully\n\n"

        user = User(content=content)
        message = Message(input=Channle.QQ, role=Role.User, content=user, output=Channle.QQ)
        async for chunk  in agent.loop(message):
                yield chunk

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",       # 防止 Nginx 等反向代理缓冲
        },
    )

@app.get("/qq")
async def qq(content: str):
    async def event_stream():
        yield ": Connected Successfully\n\n"

        user = User(content=content)
        message = Message(input=Channle.QQ, role=Role.User, content=user, output=Channle.QQ)
        async for chunk  in agent.loop(message):
                yield chunk

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

@app.get("/web")
async def web(content: str):
    async def event_stream():
        yield ": Connected Successfully\n\n"

        user = User(content=content)
        message = Message(input=Channle.WebUI, role=Role.User, content=user, output=Channle.WebUI)
        async for chunk  in agent.loop(message):
                yield chunk

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

@app.get("/clear")
def clear():
    agent.clear()

@app.get("/")
async def root():
    return {
        "status": "Ok"
    }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=int(os.getenv("agent_port", 3000)))
    
