#异步：网络请求/文件读取  I/O密集型，cup占用较小情况下   coroutine协程

# 关于异步底层原理及与操作系统相关总结
# 事件循环是由 Python 的 asyncio 库在用户态实现的，不是操作系统。
# main() 函数只是“启动者”，真正的调度者是 asyncio 的事件循环。

# 事件循环本质上就是一个 Python 层面的 while True 循环，伪代码
# # asyncio 事件循环的简化逻辑（不是真实源码）
# while True:
#     # 1. 检查有没有已经就绪的 I/O 任务（通过 epoll/kqueue/select 问操作系统）
#     ready_tasks = check_io_ready()
#
#     # 2. 把就绪的任务拿出来执行
#     for task in ready_tasks:
#         task.resume()  # 恢复协程，执行到下一个 await
#
#     # 3. 如果没任务了，就睡一会儿，等操作系统通知
#     if not ready_tasks:
#         sleep_until_io_ready()


# asyncio.run(main()) 内部实际做了三件事：
# 创建一个事件循环（调用 asyncio.new_event_loop()）
# 把 main() 这个协程包装成任务，丢进事件循环
# 启动事件循环的 while True 循环，直到所有任务完成





import asyncio

from debugpy._vendored.pydevd.pydevd_attach_to_process.winappdbg import event


# async def fetch_data(id,sleep_time):
#     print("Fetching data...")
#     await asyncio.sleep(sleep_time)
#     print("Data fetched")
#     return {f"{id},已执行完毕"}
#
# async def main():
#
#     tasks = []
#     async with asyncio.TaskGroup() as tg:
#         for i, sleep_time in enumerate([1, 2, 3,],start=1):
#             task =tg.create_task(fetch_data(i, sleep_time))
#             tasks.append(task)
#     results = [task.result() for task in tasks]
#
#     for result in results:
#         print(f"{result}")
#
#     #创建任务的方式实现
#     # task1 = asyncio.create_task(fetch_data(1,1))
#     # task2 = asyncio.create_task(fetch_data(2,2))
#     # task3 = asyncio.create_task(fetch_data(3,3))
#     #
#     #
#     # 第一个任务结束后才是第二个，依次排列
#     # result1 = await task1
#     # result2 = await task2
#     # result3 = await task3
#     # print(result1, result2, result3)
#
#     # #将所有任务集合到一起实现，缺点：如果其中一处任务出现错误不会停止
#     # result = await asyncio.gather(fetch_data(1,2),fetch_data(2,2),fetch_data(3,3))
#     # for i in result:
#     #     print(f"{i}")
#
# asyncio.run(main())

#future 对未来的一个承诺， 相当于饭店取餐码，对未来食物的一个保证，可以等待也可以做其他事，常用在底层网络库，调用函数回调
# async def set_future_result(future,value):
#     await asyncio.sleep(2)
#     future.set_result(value)
#     print(f"set_future_result {value}")
#
# async def main():
#     loop = asyncio.get_running_loop()
#     future = loop.create_future()
#
#     asyncio.create_task(set_future_result(future,"future is already"))
#
#     result = await future
#     print(f"set_future_result {result}")
#
# asyncio.run(main())


#asyncio Locky异步锁，保护的是协程（任务）不是线程，asyncio本质上是单线程并发 相当于Semaphore(1)
# 定义一个全局共享变量
# shared_resource = 0
# # 创建一个异步锁对象
# lock = asyncio.Lock()
#
# async def modify_shared_resource():
#     global shared_resource
#     # 使用异步上下文管理器获取锁
#     async with lock:
#         print(f"Resource before modification: {shared_resource}")
#         shared_resource += 1
#         await asyncio.sleep(1) # 模拟耗时的 I/O 操作
#         print(f"Resource after modification: {shared_resource}")
#
# async def main():
#     # 使用 asyncio.gather 并发启动 5 个任务
#     await asyncio.gather(*[modify_shared_resource() for _ in range(5)])
#     #流程模拟： task1进入锁，sleep挂起，自动让出事件循环的控制权，第2，3，4，5个任务趁机
#     #运行，发现锁被第一个任务占着，排队等待第一个任务结束
#
#     #如果是多线程的同步锁(如threading.lock)任务会在sleep时阻塞（卡死）整个操作系统线程，其他任务完全没法运行。
#     # threading.Lock 锁的是操作系统线程，等待时会阻塞整个线程。
# asyncio.run(main())


# semaphore 信号量:设定一次最多允许 N 个协程（任务）同时进入指定的代码块（临界区）限流并行
# 控制并发网络请求/限制数据库连接数/限制外部 API 调用频率
#核心底层原理：信号量内部维护了一个计数器
#获取（acquire）：当协程执行到 async with semaphore: 时，如果计数器 > 0，计数器减 1，协程继续执行；如果计数器 = 0，协程挂起等待（不阻塞线程）。
#释放（release）：当协程退出 async with 代码块时，计数器加 1，并唤醒一个正在排队等待的协程。
# async def access_resource(semaphore,resource_id):
#     async with semaphore:
#         print(f"Accessing resource {resource_id}")
#         await asyncio.sleep(1)
#         print(f"Released resource {resource_id}")
#
# async def main():
#     semaphore = asyncio.Semaphore(2)
#     await asyncio.gather(*(access_resource(semaphore,i) for i in range(5)))
#
#     asyncio.run(main())


# #event 事件：同步原语，协程之间的“信号通知”（通信）
# # 一个任务做完了，通知其他多个任务开始行动
# async def waiter(event):
#     print("waiting for the event to be set")
#     await event.wait() # ① 挂起自己，等待“发令枪”响起
#     print("event has been set,continuing execution")
# async def setter(event):
#     await asyncio.sleep(2) #模拟干了 2 秒的活
#     event.set()# ② 按下开关，发信号！
#     print("event has been set!")
# async def main():
#     event = asyncio.Event() # 创建一个事件对象（初始状态是“未设置/关”）
#     await asyncio.gather(waiter(event),setter(event)) # 并发启动两个任务
#
#
# asyncio.run(main())










