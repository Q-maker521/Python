from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import text

from demo_fastapi.schemas import PostCreate, PostUpdate

router = APIRouter( tags=["Posts"])

@router.get("")
async def get_posts(request: Request):
    async with request.app.state.db_engine.connect() as connection:
        result = await connection.execute(
            text("""
                SELECT id, title, content, user_id, published, created_at
                FROM posts
                ORDER BY id
            """)
        )

        posts = [dict(row) for row in result.mappings().all()]

    return {"data": posts}

@router.get("/{post_id}")
async def get_post(request: Request, post_id: int):
    async with request.app.state.db_engine.connect() as connection:
        result = await connection.execute(
            text("""
                SELECT id, title, content, user_id, published, created_at
                FROM posts
                WHERE id = :post_id
            """),
            {"post_id": post_id},
        )

        post = result.mappings().first()

    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    return {"data": dict(post)}


@router.post("", status_code=201)
async def create_post(request: Request, post: PostCreate):
    async with request.app.state.db_engine.begin() as connection:
        # 先锁定作者行，避免检查后、插入前作者被并发删除。
        user_check = await connection.execute(
            text("SELECT id FROM users WHERE id = :user_id FOR KEY SHARE"),
            {"user_id": post.user_id},
        )
        if user_check.first() is None:
            raise HTTPException(status_code=404, detail="作者用户不存在")
        result = await connection.execute(
            text("""
                INSERT INTO posts (title, content, user_id, published)
                VALUES (:title, :content, :user_id, :published)
                RETURNING id, title, content, user_id, published, created_at
            """),
            post.model_dump(),
        )
        created_post = dict(result.mappings().one())
    return {"data": created_post}


@router.put("/{post_id}")
async def update_post(request: Request, post_id: int, post: PostUpdate):
    async with request.app.state.db_engine.begin() as connection:
        result = await connection.execute(
            text("""
                UPDATE posts
                SET title = :title,
                    content = :content,
                    published = :published
                WHERE id = :post_id
                RETURNING id, title, content, user_id, published, created_at
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


@router.delete("/{post_id}", status_code=204)
async def delete_post(request: Request, post_id: int):
    async with request.app.state.db_engine.begin() as connection:
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
