from demo_no_async.demo_dectorater import *
#工具调用模拟器：函数，一个列表，列表里面是函数名和需要的参数
#工具注册表，保存函数
@my_logger
@my_timer
def search(message):
    return {"status": "success", "data": f"搜索：{message}"}

@my_logger
@my_timer
def delete(message):
    return {"status": "success", "data": f"已删除：{message}"}

@my_logger
@my_timer
def add(a,b):
    return {"status": "success", "data": a + b}

tools={
    "search":search,
    "delete":delete,
    "add":add,
}
def function_call(name,keywords=None):
    if name not in tools:
        return "error tool_name"
    if keywords is None:
        keywords={}
    try:
        return tools[name](**keywords)
    except TypeError as e:
        return  f"error parameters:{e}"


if __name__ == "__main__":
    print("测试1:", function_call("search", {"message": "Python装饰器"}))
    print("测试2:", function_call("add", {"a": 1, "b": 2}))
    print("测试3:", function_call("unknown_tool", {}))
    print(function_call("add", {"a": 1, "b": "2"}))
#预测：logging.info("%s 耗时 %.6f秒", orig_func.__name__, elapsed)
#logging.exception(f"工具 [{orig_func.__name__}] 执行失败")
#f"error parameters:{e}"