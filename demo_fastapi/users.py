import asyncio

from fastapi import APIRouter, HTTPException, Request
from pwdlib import PasswordHash
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from demo_fastapi.schemas import UserCreate, UserDataResponse, UserLogin

router = APIRouter(tags=["users"])
password_hasher = PasswordHash.recommended()

@router.post("/register", status_code=201, response_model=UserDataResponse)
async def register_user(request: Request, user: UserCreate):
    try:

        hashed_password = await asyncio.to_thread(password_hasher.hash, user.password)

        async with request.app.state.db_engine.begin() as connection:

            result = await connection.execute(
                text("""
                    INSERT INTO users (username, email, password_hash)
                    VALUES (:username, :email, :password_hash)
                    RETURNING id, username, email, created_at
                """     ),
                 {
                    "username": user.username,
                    "email": user.email,
                    "password_hash": hashed_password
                }
            )

            created_user = dict(result.mappings().one())
    except IntegrityError as exc:
        # 检查错误信息是否是邮箱或用户名重复
        if "users_email_key" in str(exc.orig) or "users_username_key" in str(exc.orig) or "uk_users_username" in str(exc.orig):
            raise HTTPException(status_code=409, detail="邮箱或用户名已存在")
        raise
    return {"data": created_user}
@router.post("/login",status_code=200, response_model=UserDataResponse)
async def login_user(request: Request, login: UserLogin):
    async with request.app.state.db_engine.connect() as connection:
        result = await connection.execute(
            text("""
                SELECT id, username, email, created_at, password_hash, disabled
                FROM users
                WHERE email = :email
            """),
            {"email": login.email},
        )
        user = result.mappings().first()
    if user is None or not user["password_hash"]:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    verified = await asyncio.to_thread(
        password_hasher.verify,
        login.password,
        user["password_hash"],
        )
    if not verified:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if user["disabled"]:
        raise HTTPException(status_code=403, detail="user is disabled")

    return {
        "data": {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "created_at": user["created_at"],
        }
    }

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
