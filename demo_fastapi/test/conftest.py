import os
from pathlib import Path
from uuid import uuid4

import pytest
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.engine import make_url

from demo_fastapi.main import create_app


@pytest.fixture
async def app():
    env_path = Path(__file__).resolve().parents[2] / ".env"
    load_dotenv(env_path)

    database_url = os.getenv("TEST_DATABASE_URL")
    if not database_url:
        raise ValueError("未配置 TEST_DATABASE_URL")

    if make_url(database_url).database != "fastapi_test":
        raise ValueError("测试必须使用 fastapi_test 数据库")

    application = create_app(database_url=database_url)

    async with application.router.lifespan_context(application):
        yield application


@pytest.fixture
async def client(app):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as http_client:
        yield http_client


@pytest.fixture
def db_engine(app):
    return app.state.db_engine

@pytest.fixture(scope="function")
async def test_user(client):
    """管理测试用户的生命周期"""
    # 1. 创建用户
    token = uuid4().hex
    payload = {"username": f"test_{token}", "email": f"{token}@example.com", "password": "password123"}
    res = await client.post("/users/register", json=payload)
    # 建议断言注册成功(状态码已改为201)
    assert res.status_code == 201, res.text
    user_id = res.json()["data"]["id"]

    yield user_id

    # 只负责删用户。帖子由 test_post fixture 负责清理（它先销毁）
    res_delete = await client.delete(f"/users/{user_id}")
    assert res_delete.status_code == 204, res_delete.text

@pytest.fixture(scope="function")
async def test_post(client, test_user):
    """管理测试帖子的生命周期"""
    # 1. 创建关联帖子
    payload = {
        "title": "测试标题",
        "content": "测试内容",
        "published": False,
        "user_id": test_user
    }
    res = await client.post("/posts", json=payload)
    assert res.status_code == 201, res.text
    post_id = res.json()["data"]["id"]

    yield post_id

    # 2. yield 后测试失败也会执行清理；yield 前失败不执行此段。
    res_delete = await client.delete(f"/posts/{post_id}")
    assert res_delete.status_code in [204, 404], res_delete.text
