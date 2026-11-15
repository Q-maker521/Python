import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


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

