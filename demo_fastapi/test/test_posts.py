from pwdlib import PasswordHash
from sqlalchemy import text
import pytest
from uuid import uuid4



password_hash = PasswordHash.recommended()

async def test_posts_crud(client,test_post):
    post_id = test_post
    response = await client.get(f"/posts/{post_id}")
    assert response.status_code == 200, response.text
    created = response.json()["data"]

    # 更新
    payload = {
        "title": "更新后的标题",
        "content": "更新后的内容",
        "published": True,
    }
    response = await client.put(
        f"/posts/{post_id}", json=payload
    )
    assert response.status_code == 200, response.text
    updated = response.json()["data"]

    for key, value in payload.items():
        assert updated[key] == value
    assert updated["id"] == post_id
    assert updated["created_at"] == created["created_at"]

    # 再次查询，确认更新已保存
    response = await client.get(f"/posts/{post_id}")
    assert response.status_code == 200, response.text
    assert response.json()["data"] == updated

    # 删除：204 不应该有响应体
    response = await client.delete(f"/posts/{post_id}")
    assert response.status_code == 204, response.text
    assert response.content == b""

    # 删除后查询、更新和再次删除，都应返回 404
    response = await client.get(f"/posts/{post_id}")
    assert response.status_code == 404, response.text

    response = await client.put(
        f"/posts/{post_id}", json=payload
    )
    assert response.status_code == 404, response.text

    response = await client.delete(f"/posts/{post_id}")
    assert response.status_code == 404, response.text

async def test_register_duplicate_email(client, db_engine):
    from uuid import uuid4
    token = uuid4().hex
    payload = {"username": f"test_{token}", "email": f"{token}@example.com", "password": "password123"}
    res = await client.post("/users/register", json=payload)
    assert res.status_code == 201, res.text
    data = res.json()["data"]
    user_id = data["id"]
    try:

        assert "password" not in data
        assert "password_hash" not in data

        async with db_engine.connect() as connection:
            result = await connection.execute(text("SELECT password_hash FROM users WHERE id = :user_id"), {"user_id": user_id})
            stored_hash = result.scalar_one()

        assert stored_hash
        assert stored_hash != payload["password"]
        assert password_hash.verify("password123", stored_hash)
        assert not password_hash.verify("wrong-password", stored_hash)

        payload["username"] += "_other"
        duplicate = await client.post("/users/register", json=payload)
        assert duplicate.status_code == 409, duplicate.text

    finally:
        deleted = await client.delete(f"/users/{user_id}")
        assert deleted.status_code == 204, deleted.text

@pytest.mark.parametrize(
    "scenario, expected_status",
    [
        ("success", 200),
        ("wrong_password", 401),
        ("missing_user", 401),
        ("missing_hash", 401),
        ("disabled", 403),
    ],
)
async def test_login(client, db_engine, scenario, expected_status):
    token = uuid4().hex
    payload = {
        "username": f"test_{token}",
        "email": f"{token}@example.com",
        "password": "password123",
    }

    # 每个场景独立创建用户
    registered = await client.post("/users/register", json=payload)
    assert registered.status_code == 201, registered.text
    user_id = registered.json()["data"]["id"]

    try:
        login_payload = {
            "email": payload["email"],
            "password": payload["password"],
        }

        if scenario == "wrong_password":
            login_payload["password"] = "wrong-password"

        elif scenario == "missing_user":
            # 删除刚创建的用户，确保这个邮箱对应的用户不存在
            deleted = await client.delete(f"/users/{user_id}")
            assert deleted.status_code == 204, deleted.text

        elif scenario == "missing_hash":
            async with db_engine.begin() as connection:
                await connection.execute(
                    text("""
                        UPDATE users
                        SET password_hash = NULL
                        WHERE id = :user_id
                    """),
                    {"user_id": user_id},
                )

        elif scenario == "disabled":
            async with db_engine.begin() as connection:
                await connection.execute(
                    text("""
                        UPDATE users
                        SET disabled = TRUE
                        WHERE id = :user_id
                    """),
                    {"user_id": user_id},
                )

        # 数据库修改已提交，再发送登录请求
        response = await client.post("/users/login", json=login_payload)
        assert response.status_code == expected_status, response.text

        if expected_status == 200:
            data = response.json()["data"]
            assert data["id"] == user_id
            assert data["username"] == payload["username"]
            assert data["email"] == payload["email"]
            assert "password" not in data
            assert "password_hash" not in data

        elif expected_status == 401:
            assert response.json()["detail"] == "Invalid email or password"

        else:
            assert response.json()["detail"] == "user is disabled"

    finally:
        deleted = await client.delete(f"/users/{user_id}")
        # missing_user 场景中，用户此前已被删除
        expected_delete = 404 if scenario == "missing_user" else 204
        assert deleted.status_code == expected_delete, deleted.text


async def test_create_post_invalid_user(client):
    # 创建再删除，使用确定不存在的 ID，而不是猜测 99999。
    from uuid import uuid4
    token = uuid4().hex
    res = await client.post("/users/register", json={
        "username": f"test_{token}", "email": f"{token}@example.com", "password": "password123"
    })
    assert res.status_code == 201, res.text
    user_id = res.json()["data"]["id"]
    deleted = await client.delete(f"/users/{user_id}")
    assert deleted.status_code == 204, deleted.text
    res = await client.post("/posts", json={
        "title": "无效用户帖子", "content": "内容",
        "published": False, "user_id": user_id,
    })
    assert res.status_code == 404, res.text
