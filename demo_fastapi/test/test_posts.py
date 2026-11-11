async def test_posts_crud(client):
    # 创建：使用数据库生成的 ID
    response = await client.post(
        "/posts",
        json={
            "title": "测试标题",
            "content": "测试内容",
            "published": False,
        },
    )
    assert response.status_code == 201, response.text
    created = response.json()["data"]
    post_id = created["id"]

    try:
        # 查询
        response = await client.get(f"/posts/{post_id}")
        assert response.status_code == 200, response.text
        assert response.json()["data"] == created

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

    finally:
        # 中途断言失败，也尝试清理本测试创建的记录
        # 已删除时再次调用会返回 404，这是正常情况
        await client.delete(f"/posts/{post_id}")