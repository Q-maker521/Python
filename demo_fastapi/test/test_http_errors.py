import httpx
import pytest




cases = [
    ("缺少参数", {"name": "add", "arguments": {"a": 1}}, 422, "b"),
    ("正常加法", {"name": "add", "arguments": {"a": 1, "b": 2}}, 200, None),
    ("未知工具", {"name": "not_exist", "arguments": {}}, 404, "未知工具"),
    ("执行失败", {"name": "search", "arguments": {"message": "失败测试"}}, 500, "工具执行失败"),
    ("执行超时", {"name": "search", "arguments": {"message": "慢请求"}}, 504, "超过两秒"),
    ]
@pytest.mark.parametrize(
    "label, payload, expected_status, detail",
    cases,
    ids=[case[0] for case in cases]
)
async def test_http_errors(client,label, payload, expected_status, detail):

    
    response = await client.post(
        "tools/execute_with_timeout", json=payload,
    )

    assert response.status_code == expected_status, (label, response.text)
    body = response.json()

    if expected_status == 200:
        assert body["status"] == "success", body
        assert body["data"] == 3, body
    else:
        assert detail in body["detail"], body
        print(f"{label}测试通过")



