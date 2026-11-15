import asyncio
import json
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from async_demo.demo_json_async import function_call, handle_request_with_timeout
from demo_fastapi.database import lifespan
from demo_fastapi.posts import router as posts_router
from demo_fastapi.schemas import ToolPreviewResponse, ToolRequest
from demo_fastapi.users import router as users_router

load_dotenv()


def create_app(database_url: str | None = None):
    app = FastAPI(lifespan=lifespan)
    # 状态挂载
    app.state.database_url = database_url

    tool_semaphore = asyncio.Semaphore(2)

    @app.get("/")
    async def health():
        return {"message": "Health check passed"}


    @app.post("/tools/preview", response_model=ToolPreviewResponse)
    async def preview_tool(request: ToolRequest):
        return {
            "status": "received",
            "name": request.name,
            "arguments": request.arguments
        }

    @app.post("/tools/execute", response_model=dict[str, Any])
    async def execute_tool(request: ToolRequest):
        return await function_call(request.name, request.arguments)

    @app.post("/tools/execute_with_timeout")
    async def execute_tool_with_timeout(request: ToolRequest):
        result = await handle_request_with_timeout(
            json.dumps(request.model_dump(), ensure_ascii=False),
            tool_semaphore,
        )
        #超时状态码：504
        if result.get("status") == "timeout":
            raise HTTPException(
                status_code=504,
                detail=result.get("message", "Request timed out"),
            )
        #参数错误(缺少参数)状态码：422
        if result.get("code") == "invalid_arguments":
            raise HTTPException(
                status_code=422,
                detail=result["message"],
            )

        #工具不存在状态码：404
        if result.get("code") == "unknown_tool":
            raise HTTPException(
                status_code=404,
                detail=result["message"],
            )
        #工具执行失败状态码：500
        if result.get("code") == "execution_error":
            raise HTTPException(
                status_code=500,
                detail=result["message"],
            )
        return result

    # 统一在 main.py 中注册路由、声明前缀和标签
    app.include_router(posts_router, prefix="/posts", tags=["Posts"])
    app.include_router(users_router, prefix="/users", tags=["users"])

    return app

app = create_app()
