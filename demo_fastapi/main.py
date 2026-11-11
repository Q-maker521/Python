import asyncio
import json
from typing import Any, Literal
# from asyncpg import Pool, create_pool  # 导入 asyncpg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from async_demo.demo_json_async import function_call
from async_demo.demo_json_async import handle_request_with_timeout




# 客户端需要传入参数
class ToolRequest(BaseModel):
    name: str = Field(min_length=1)
    arguments: dict[str, Any]

#服务器预览接口返回参数
class ToolPreviewResponse(BaseModel):
    status: Literal["received"]
    name: str
    arguments: dict[str, Any]



def create_app():
    app = FastAPI()
    tool_semaphore = asyncio.Semaphore(2)
# # 创建一个连接池变量
# pool: Pool = None

# @app.on_event("startup")
# async def startup():
#     global pool
#     # 根据你的 DataGrip 配置(dbname=fastapi, user=postgres)初始化连接池
#     pool = await create_pool(
#         database="fastapi",
#         user="postgres",
#         password="你的数据库密码",
#         host="localhost"
#     )

# @app.on_event("shutdown")
# async def shutdown():
#     # 关闭连接池
#     await pool.close()

# @app.get("/")
# async def health():
#     return {"message": "Health check passed"}

# # 新增：测试数据库连接的接口
# @app.get("/test-db")
# async def test_db():
#     if not pool:
#         return {"status": "error", "message": "数据库连接池未初始化"}

#     async with pool.acquire() as conn:
#         # 查询你之前在 DataGrip 中创建的 products 表
#         rows = await conn.fetch("SELECT name, price FROM products LIMIT 5")

#     return {"status": "success", "data": [dict(row) for row in rows]}






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
    return app


app = create_app()
