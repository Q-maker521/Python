import pytest
from httpx import ASGITransport, AsyncClient
from demo_fastapi.main import app

@pytest.fixture
async def client():

    # 使用 ASGITransport 将请求直接转发给 FastAPI 应用
    transport = ASGITransport(app=app)
    
    #base_url 是必须的（即使不走真实网络），httpx 需要它来构建绝对 URL
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    # 清理资源：上下文退出时自动关闭客户端连接 