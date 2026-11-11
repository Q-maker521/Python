import asyncio
import httpx
import pytest
import time



@pytest.mark.parametrize("round_id", [1, 2])
async def  test_execute_with_timeout_concurrency(client, round_id):
    keywords = ["Python", "FastAPI", "Agent","慢请求","rust"]

    

    start_time = time.perf_counter()
        #并发执行多个请求
    responses= await asyncio.gather(
        *[
            client.post(
                "/tools/execute_with_timeout",
                json={"name": "search", "arguments": {"message": keyword}},
            )
            for keyword in keywords
        ]
    )

    elapsed = time.perf_counter() - start_time

    for keyword, response in zip(keywords, responses):
        body = response.json()

        if keyword == "慢请求":
            assert response.status_code == 504, response.text
            assert "超过两秒" in body["detail"]
        else:
            assert response.status_code == 200, response.text
            assert body["status"] == "success"
            assert body["data"] == f"搜索：{keyword}"

        print(keyword, response.status_code, body)

    print(f"并发总耗时：{elapsed:.3f} 秒")
    print("并发测试通过")
