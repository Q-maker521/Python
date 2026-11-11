import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.engine import make_url

from demo_fastapi.main import create_app


@pytest.fixture
async def client():
    # conftest.py 位于 demo_fastapi/test/，所以向上两级到项目根目录
    env_path = Path(__file__).resolve().parents[2] / ".env"
    load_dotenv(env_path)

    database_url = os.getenv("TEST_DATABASE_URL")
    if not database_url:
        raise ValueError("未找到 TEST_DATABASE_URL 环境变量")

    # 避免误连日常使用的数据库
    if make_url(database_url).database != "fastapi_test":
        raise ValueError("测试必须使用 fastapi_test 数据库")

    app = create_app(database_url=database_url)

    # 进入时执行 lifespan 中 yield 前的初始化
    # 退出时执行 finally，释放数据库连接池
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as http_client:
            yield http_client