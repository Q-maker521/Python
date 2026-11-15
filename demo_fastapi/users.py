from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from demo_fastapi.schemas import UserCreate

router = APIRouter(tags=["users"])

@router.post("/register", status_code=201)
async def register_user(request: Request, user: UserCreate):
    try:
        async with request.app.state.db_engine.begin() as connection:

            result = await connection.execute(
                text("""
                    INSERT INTO users (username, email)
                    VALUES (:username, :email)
                    RETURNING id, username, email
                """     ),
                user.model_dump(),
            )
            created_user = dict(result.mappings().one())
    except IntegrityError as exc:
        # 检查错误信息是否是邮箱或用户名重复
        if "users_email_key" in str(exc.orig) or "users_username_key" in str(exc.orig) or "uk_users_username" in str(exc.orig):
            raise HTTPException(status_code=409, detail="邮箱或用户名已存在")
        raise
    return {"data": created_user}
@router.post("/login")
async def login_user(request: Request,username:str,email:str):
    async with request.app.state.db_engine.begin() as connection:
        result = await connection.execute(
            text("""
                SELECT id, username, email
                FROM users
                WHERE username = :username AND email = :email
            """),
            {"username": username, "email": email},
        )
        user = result.mappings().first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid username or email")
        user = dict(user)

    return {"data": user}
@router.delete("/{user_id}", status_code=204)
async def delete_user(request: Request, user_id: int):
    async with request.app.state.db_engine.begin() as connection:
        result = await connection.execute(
            text("""
                SELECT id, username, email
                FROM users
                WHERE id = :user_id
            """),
            {"user_id": user_id},
        )
        user = result.mappings().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        await connection.execute(
            text("""
                DELETE FROM users
                WHERE id = :user_id
            """),
            {"user_id": user_id},
        )
    return None
