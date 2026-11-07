import json
import asyncio
import time
from async_demo.demo_function_call_async import *


#从同步到异步：
# 改变：def handle_request(request_json)：-》  async def handle_request(request_json):   让handle_request成为一个异步函数
#     return function_call(name,arguments)-》return await function_call(name,arguments)

# ① 同步版本（原来）的执行过程
# 假设 function_call 内部是一个网络请求（比如调用某个 API，需要 2 秒才返回）：
# 当 10 个用户同时发来请求：
# 用户 A 的请求进来 → 执行到 function_call → 卡住等 2 秒→ 返回结果
# 用户 B 的请求进来 → 执行到 function_call → 再卡住等 2 秒→ 返回结果
# ……用户 C、D、E 全部排队，每人等 2 秒，总共要 20 秒才能处理完。
# ② 异步版本（现在）的执行过程
# 用户 A 的请求进来 → 执行到 await function_call → Python 说：“我在等网络，先去干别的→ 控制权交还给事件循环
# 事件循环立刻去处理用户 B 的请求 → 同样遇到 await → 再去处理 C……
# 2 秒后，A 的网络请求回来了，事件循环回来把结果返回给 A。
# 总共只用了 2 秒，10 个用户全部处理完毕
# 这就是异步的核心价值：在等待 I/O（网络、文件、数据库）的时候，不傻等，去处理别的任务，从而实现单线程高并发。
#
# 改造前：整个 handle_request 是同步的，调用它就会阻塞整个线程
# 改造后：handle_request 变成了一个“可以暂停”的协程。当它在等 function_call 的结果时，Python 可以去处理其他请求，大大提升效率

async def handle_request(request_json):
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
        # 关键改动：加了 await
        return await function_call(name,arguments)
    except json.decoder.JSONDecodeError:
        return "错误：json格式不正确"
    except Exception as e:
        return f"发生未知错误：{e}"

#设置超时函数
async def handle_request_with_timeout(request_json):
    try:
        return await asyncio.wait_for(handle_request(request_json),timeout=2)
    except asyncio.TimeoutError:
        return {
            "status": "timeout",
            "message": "请求执行过程超过两秒",
        }

def  mock_model(user_input):
    if user_input.startswith("搜索"):
        key = user_input.removeprefix("搜索").strip()

        request = {
            "name": "search",
            "arguments": {"message": key}
        }

        return  json.dumps(request, ensure_ascii=False)

    return None

requests1 = [
    json.dumps({
        "name": "search",
        "arguments": {"message": keyword}
    }, ensure_ascii=False)
    for keyword in ["Python", "FastAPI", "Agent"]
]
async  def main():

    #在 for 循环中逐个等待请求完成，所以这三个请求串行执行。 等待期间，事件循环仍可运行其他已调度的任务。
    # start = time.perf_counter()
    # for request in requests:
    #     result = await handle_request(request)
    #     print(result)
    # print("串行总耗时：", time.perf_counter() - start)

    # start = time.perf_counter()
    # # asyncio.gather会一次性把这三个handle_request协程任务同时提交给事件循环
    # results = await asyncio.gather(
    #     *(handle_request(request) for request in requests)
    # )
    # for result in results:
    #     print(result)
    # print("并发总耗时：", time.perf_counter() - start)


    requests = [
        json.dumps({
            "name": "search",
            "arguments": {"message": keyword}
        }, ensure_ascii=False)
        for keyword in ["Python", "慢请求", "Agent"]
    ]
    start = time.perf_counter()
    results = await asyncio.gather(
        *(handle_request_with_timeout(request) for request in requests)
    )

    for result in results:
        print("执行结果", result)

    print("开发总耗时：",time.perf_counter() - start)


    # #失败测试：gather组中默认设置一旦有一个异常，终止
    # start = time.perf_counter()
    # results = await asyncio.gather(
    #     search("Python"),
    #     search("失败测试"),
    #     search("Agent"),return_exceptions=True#开启后除指定模拟失败外，其余两个搜索均成功执行
    # # return_exceptions=True  # 先不开启，测试默认行为
    # )
    # for res in results:
    #     print(f"{res}")
    # print("并发总耗时:", time.perf_counter() - start)

asyncio.run(main())


# start = time.perf_counter()
# for request in requests:
#     result = await handle_request(request)
#     print(result)
# print("串行总耗时：", time.perf_counter() - start)


# user_input = input("请输入需求：")
# request_json1 = mock_model(user_input)
# if request_json1 is None:
#     print("暂时只支持搜索关键词")
# else:
#     print("生成的请求：", request_json1)
#     print("执行结果：",handle_request(request_json1))


#print(handle_request('{"name":"search","arguments":{"message":"Agent"}}'))
#print(handle_request('这不是JSON'))
#print(handle_request('[]'))
#print(handle_request('{"arguments":{}}'))
#print(handle_request('{"name":"search","arguments":"Agent"}'))
#print(handle_request('{"name":123,"arguments":{}}'))
#print(handle_request('{"name":"   ","arguments":{}}'))
#print(handle_request('{"name":[],"arguments":{}}'))
