import asyncio
import inspect
import time
from async_demo.demo_dectorater_async import *
#工具调用模拟器：函数，一个列表，列表里面是函数名和需要的参数
#工具注册表，保存函数

# 创建信号量，限制最大并发数为 2
semaphore = asyncio.Semaphore(2)

@my_logger
@my_timer
async def search(message):
        if message == "失败测试":
            raise ValueError("模拟搜索失败")

        delay = 5 if message == "慢请求" else 1
        await asyncio.sleep(delay)
        return {"status": "success", "data": f"搜索：{message}"}

@my_logger
@my_timer
async def delete(message):
    return {"status": "success", "data": f"已删除：{message}"}

@my_logger
@my_timer
async def add(a,b):
    return {"status": "success", "data": a + b}

tools={
    "search":search,
    "delete":delete,
    "add":add,
}
async def function_call(name,keywords=None):
    if keywords is None:
        keywords={}

    #细化返回参数处理
    if name not in tools:
         return {
            "status": "error",
            "code": "unknown_tool",
            "message": f"未知工具：{name}",
        }

    tool = tools[name]

    # 只检查参数是否能匹配函数签名
    try:
        inspect.signature(tool).bind(**keywords)
    except TypeError as e:
       return {
            "status": "error",
            "code": "invalid_arguments",
            "message": str(e),
    }

    return await tool(**keywords)


#定义带超时控制的包装函数
async def search_with_timeout(msg):
    try :
        # 设置2秒超时
        return await asyncio.wait_for(search(msg), timeout=2)
    except asyncio.TimeoutError:
        return {
            "status": "timeout",
            "message": f"请求 {msg} 超过 2 秒",
        }
async def main():
    start = time.perf_counter()



    result = await asyncio.gather(
        search_with_timeout("python"),
        search_with_timeout("慢请求"),
        search_with_timeout("Agent"),
        return_exceptions=True
    )
    for res in result:
        print(f"执行结果：{res}")
    print("并发总共耗时：", time.perf_counter() - start)


#限制并发数为2
# async def main():
#
#     requests=["python","java","cpp","go","ruby"]
#     start = time.perf_counter()
#
#     tasks = [search(f"{x}")for x in requests]
#     results = await asyncio.gather(*tasks, return_exceptions=True)
#
#     for result in results:
#         print(result)
#
#     print("并发总耗时：", time.perf_counter() - start)



if __name__ == "__main__":
    asyncio.run(main())


# if __name__ == "__main__":
#     print("测试1:", function_call("search", {"message": "Python装饰器"}))
#     print("测试2:", function_call("add", {"a": 1, "b": 2}))
#     print("测试3:", function_call("unknown_tool", {}))
#     print(function_call("add", {"a": 1, "b": "2"}))
# #预测：logging.info("%s 耗时 %.6f秒", orig_func.__name__, elapsed)
# #logging.exception(f"工具 [{orig_func.__name__}] 执行失败")
# #f"error parameters:{e}"