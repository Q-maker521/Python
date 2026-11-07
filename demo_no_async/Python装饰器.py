#装饰器的作用：在不修改原函数代码、不改变原函数调用方式的前提下，给函数增加额外功能
#相当于一个新函数，接收一个函数再返回一个新函数，新函数内部可以执行额外逻辑（前置/后置），调用原来函数，修改参数，返回值，捕获异常等
#常见场景：日志打印、性能计时、权限校验、缓存、异常捕获
#手写装饰器timer,统计函数执行耗时
import time
import functools
def timer(func):
    ##保留原函数的名字、文档字符串
    @functools.wraps(func)
    def wrapper(*args,**kwargs):
        #记录开始时间
        start = time.time()
        #执行原函数，接收返回值
        result = func(*args,**kwargs)
        #记录结束时间
        end = time.time()
        #打印耗时
        print(f"函数【{func.__name__}】执行耗时：{end-start:.6f}秒")
        #返回原函数结果
        return result
    return wrapper
@timer
def sleep_func(sec):
    time.sleep(sec)
    return "执行完成"
print(sleep_func(1))
@timer
def calc_sum(n):
    s=0
    for i in range(1,n+1):
        s=s+i
    return s
print(calc_sum(10000))