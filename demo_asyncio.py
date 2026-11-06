#异步：网络请求/文件读取  I/O密集型，cup占用较小情况下   coroutine协程

import asyncio

async def fetch_data(id,sleep_time):
    print("Fetching data...")
    await asyncio.sleep(sleep_time)
    print("Data fetched")
    return {f"{id},已执行完毕"}

async def main():


    tasks = []
    async with asyncio.TaskGroup() as tg:
        for i, sleep_time in enumerate([1, 2, 3,],start=1):
            task =tg.create_task(fetch_data(i, sleep_time))
            tasks.append(task)
    results = [task.result() for task in tasks]

    for result in results:
        print(f"{result}")

    #创建任务的方式实现
    # task1 = asyncio.create_task(fetch_data(1,1))
    # task2 = asyncio.create_task(fetch_data(2,2))
    # task3 = asyncio.create_task(fetch_data(3,3))
    #
    #
    # 第一个任务结束后才是第二个，依次排列
    # result1 = await task1
    # result2 = await task2
    # result3 = await task3
    # print(result1, result2, result3)

    # #将所有任务集合到一起实现，缺点：如果其中一处任务出现错误不会停止
    # result = await asyncio.gather(fetch_data(1,2),fetch_data(2,2),fetch_data(3,3))
    # for i in result:
    #     print(f"{i}")



asyncio.run(main())








async def set_future_result(future,value):
    await asyncio.sleep(2)
    future.set_result(value)
    print(f"set_future_result {value}")


async def main():
    loop = asyncio.get_running_loop()
    future = loop.create_future()

    asyncio.create_task(set_future_result(future,"future is already"))

    result = await future
    print(f"set_future_result {result}")

asyncio.run(main())
