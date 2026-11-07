import asyncio
from functools import wraps
import logging
# 配置日志：输出到文件，同时输出到终端（StreamHandler）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../app.log', encoding='utf-8'),  # 写文件
        logging.StreamHandler()                       # 打印到终端
    ]
)

#第一次代码改动：def my_logger(orig_func):-》async def my_logger(orig_func):致命错误，被async修饰的函数在执行时返回一个协程对象，而不是返回内部函数
#             def my_timer(orig_func):-》async def my_timer(orig_func):

#正确改法：只修改wrapper函数
def my_logger(orig_func): # 普通函数：接收原函数，返回包装函数
     @wraps(orig_func)
     async def wrapper(*args, **kwargs):# 异步包装函数
        try:
            logging.info(
                f"工具: {orig_func.__name__}, 开始执行..."
            )
            #在执行原函数阶段添加await
            result = await orig_func(*args, **kwargs)
            logging.info(
                 f"工具：{orig_func.__name__},执行成功,结果{result}"
            )
            return result# 返回函数，不是协程对象
        except asyncio.CancelledError:
            logging.warning(f"工具{orig_func.__name__}被取消",)
            raise
        except Exception :
            logging.exception(f"工具 [{orig_func.__name__}] 执行失败")
            raise #重新抛出异常，交给外层处理
     return wrapper
def my_timer(orig_func):
    import time

    @wraps(orig_func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return await orig_func(*args, **kwargs)
        finally:
            elapsed = time.perf_counter() - start
            logging.info("%s 耗时 %.6f秒", orig_func.__name__, elapsed)
    return wrapper






# def decorator_function(original_function):
#     @wraps(original_function)
#     def wrapper_function(*args, **kwargs):
#         print("decorator function run")
#         result = original_function(*args, **kwargs)  # 调用原函数
#         print("decorator function stop")
#     return wrapper_function
#
# class decorator_class(object):
#     def __init__(self,original_function):
#         self.original_function = original_function
#         self.__name__ = original_function.__name__
#         self.__doc__ = original_function.__doc__
#
#     def __call__(self, *args, **kwargs):
#         print(f"call method executed this before {self.original_function.__name__}")
#         return self.original_function(*args, **kwargs)
#
# @decorator_function
# def display():
#     print("i am working")
#
# @decorator_function
# def display2(name:str,age:int):
#     print (f"my name is {name} and my age is {age} ")

# display2("john",16)
# print(display2.__name__)
#



# @my_timer
# @my_logger
# def add(x,y):
#     return x+y
#
# add(1,2)