import pytest
import httpx

@pytest.fixture
async def client():
    # 准备资源：创建异步 HTTP 客户端
    async with httpx.AsyncClient(timeout=15.0, base_url="http://127.0.0.1:8000") as client:
        # 提供给测试：将客户端实例注入测试函数
        yield client
    # 清理资源：上下文退出时自动关闭客户端连接 