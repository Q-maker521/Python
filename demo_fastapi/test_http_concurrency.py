import asyncio
import json
import httpx
import time


async def main():
    keywords = ["Python", "FastAPI", "Agent","慢请求","rust"]

    async with httpx.AsyncClient(timeout=15.0) as client:
        start = time.perf_counter()

        responses = await asyncio.gather(
            *(
                client.post(
                    "http://localhost:8000/tools/execute_with_timeout",
                    json={
                        "name": "search",
                        "arguments": {"message": keyword},
                    },
                )
                for keyword in keywords
            )
        )

        for keyword,response in zip(keywords,responses):
            print(keyword,response.status_code,response.json())

        print("并发总耗时：", time.perf_counter() - start)


if __name__ == "__main__":
    asyncio.run(main())
