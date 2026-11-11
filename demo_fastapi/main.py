import asyncio
import json
import os

from pathlib import Path
from typing import Any, Literal
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

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


class PostCreate(BaseModel):
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    published: bool = False 


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 服务启动时执行
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(env_path)

    database_url = app.state.database_url
    if database_url is None:
        database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("未配置数据库连接地址，请检查 DATABASE_URL")

    engine = create_async_engine(database_url)

    try:
        # 启动时验证连接，失败则不继续启动服务
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))

        # 保存到当前应用，供接口使用
        app.state.db_engine = engine

        yield  # 服务在这里运行、接收请求

    finally:
        # 服务关闭时释放数据库连接池
        await engine.dispose()



def create_app(database_url: str | None = None):
    app = FastAPI(lifespan=lifespan)
    app.state.database_url = database_url
    tool_semaphore = asyncio.Semaphore(2)

    @app.get("/posts")
    async def get_posts():
        async with app.state.db_engine.connect() as connection:
            result = await connection.execute(
                text("""
                    SELECT id, title, content, published, created_at
                    FROM posts
                    ORDER BY id
                """)
            )

            posts = [dict(row) for row in result.mappings().all()]

        return {"data": posts}

    @app.get("/posts/{post_id}")
    async def get_post(post_id: int):
        async with app.state.db_engine.connect() as connection:
            result = await connection.execute(
                text("""
                    SELECT id, title, content, published, created_at
                    FROM posts
                    WHERE id = :post_id
                """),
                {"post_id": post_id},
            )

            post = result.mappings().first()

        if post is None:
            raise HTTPException(status_code=404, detail="Post not found")

        return {"data": dict(post)}


    @app.post("/posts", status_code=201)
    async def create_post(post: PostCreate):
        async with app.state.db_engine.begin() as connection:
            result = await connection.execute(
                text("""
                    INSERT INTO posts (title, content, published)
                    VALUES (:title, :content, :published)
                    RETURNING id, title, content, published, created_at
                """),
                post.model_dump(),
            )
            created_post = dict(result.mappings().one())

        return {"data": created_post}

    @app.put("/posts/{post_id}")
    async def update_post(post_id: int, post: PostCreate):
        async with app.state.db_engine.begin() as connection:
            result = await connection.execute(
                text("""
                    UPDATE posts
                    SET title = :title,
                        content = :content,
                        published = :published
                    WHERE id = :post_id
                    RETURNING id, title, content, published, created_at
                """),
                {
                    **post.model_dump(), 
                    "post_id": post_id
                },
            )
            updated_post = result.mappings().first()
            if updated_post is None:
                raise HTTPException(
                    status_code=404,
                    detail="Post not found",
                )
        
        return {"data": dict(updated_post)}


    @app.delete("/posts/{post_id}", status_code=204)
    async def delete_post(post_id: int):
        async with app.state.db_engine.begin() as connection:
            result = await connection.execute(
                text("""
                    DELETE FROM posts
                    WHERE id = :post_id
                """),
                {"post_id": post_id},
            )
            if result.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail="Post not found",
                )
        



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
