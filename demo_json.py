import json
from demo_function_call import function_call

def handle_request(request_json):
    try:
        request = json.loads(request_json)
        if not isinstance(request, dict):
            return "请求必须是字典"
        name = request.get("name")
        arguments = request.get("arguments")
        if not isinstance(name, str) or not name.strip():
            return "工具名称必须是非空字符串"
        if not isinstance(arguments, dict):
            return "参数必须是字典"
        return function_call(name,arguments)
    except json.decoder.JSONDecodeError:
        return "错误：json格式不正确"
    except Exception as e:
        return f"发生未知错误：{e}"

def mock_model(user_input):
    if user_input.startswith("搜索"):
        key = user_input.removeprefix("搜索").strip()

        request = {
            "name": "search",
            "arguments": {"message": key}
        }

        return json.dumps(request, ensure_ascii=False)

    return None

user_input = input("请输入需求：")
request_json1 = mock_model(user_input)
if request_json1 is None:
    print("暂时只支持搜索关键词")
else:
    print("生成的请求：", request_json1)
    print("执行结果：",handle_request(request_json1))






#print(handle_request('{"name":"search","arguments":{"message":"Agent"}}'))
#print(handle_request('这不是JSON'))
#print(handle_request('[]'))
#print(handle_request('{"arguments":{}}'))
#print(handle_request('{"name":"search","arguments":"Agent"}'))
#print(handle_request('{"name":123,"arguments":{}}'))
#print(handle_request('{"name":"   ","arguments":{}}'))
#print(handle_request('{"name":[],"arguments":{}}'))
