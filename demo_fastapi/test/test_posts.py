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

async def test_register_duplicate_email(client):
    from uuid import uuid4
    token = uuid4().hex
    payload = {"username": f"test_{token}", "email": f"{token}@example.com"}
    res = await client.post("/users/register", json=payload)
    assert res.status_code == 201, res.text
    user_id = res.json()["data"]["id"]
    try:
        payload["username"] += "_other"
        duplicate = await client.post("/users/register", json=payload)
        assert duplicate.status_code == 409, duplicate.text
    finally:
        deleted = await client.delete(f"/users/{user_id}")
        assert deleted.status_code == 204, deleted.text


async def test_create_post_invalid_user(client):
    # 创建再删除，使用确定不存在的 ID，而不是猜测 99999。
    from uuid import uuid4
    token = uuid4().hex
    res = await client.post("/users/register", json={
        "username": f"test_{token}", "email": f"{token}@example.com",
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
