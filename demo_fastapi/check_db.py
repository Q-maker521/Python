import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


async def main():
    # check_db.py 上两级目录就是项目根目录
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(env_path)

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("未找到 DATABASE_URL 环境变量")

    engine = create_async_engine(database_url)

    try:
        # 从引擎获取一个连接，退出 async with 时归还连接
        async with engine.connect() as connection:
            result = await connection.execute(text("SELECT 1"))
            print("连接验证：", result.scalar_one())

            result = await connection.execute(
                text("""
                    SELECT id, title, content, published, created_at
                    FROM posts
                    ORDER BY id
                """)
            )

            posts = [dict(row) for row in result.mappings().all()]

            print(f"读取到 {len(posts)} 条帖子：")
            for post in posts:
                print(post)

    finally:
        # 无论查询成功还是失败，都释放连接池资源
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())