# Asyncio 完全教学指南

## 什么是 Asyncio？

`asyncio` 是 Python 的异步编程库，用于编写并发代码。它允许你在**单个线程**中运行**多个任务**，通过在任务之间**快速切换**来实现并发效果。

### 核心概念对比

```
同步（Synchronous）：
任务1 ─→ 任务2 ─→ 任务3
|      |      |
10s    10s    10s
总耗时：30s

异步（Asynchronous）：
任务1 ↓ 任务2 ↓ 任务3
 ↓    ↓    ↓
 等待中...    (同时进行)
总耗时：10s （最长的任务耗时）
```

---

## 1️⃣ 基础：async/await

### 1.1 定义异步函数

```python
# 同步函数
def fetch_data():
    """同步获取数据（会阻塞）"""
    time.sleep(2)  # 阻塞 2 秒
    return "data"

# 异步函数
async def fetch_data_async():
    """异步获取数据（不阻塞）"""
    await asyncio.sleep(2)  # 等待 2 秒，期间可处理其他任务
    return "data"
```

### 1.2 运行异步函数

```python
import asyncio

async def main():
    result = await fetch_data_async()
    print(result)  # "data"

# 方式1：使用 asyncio.run()（Python 3.7+）
asyncio.run(main())

# 方式2：获取事件循环（老方式）
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```

---

## 2️⃣ 常用用法

### 2.1 创建后台任务（不等待）- create_task()

**场景**：启动任务但不需要等待结果

```python
import asyncio

async def background_job(name):
    """后台任务"""
    print(f"[{name}] 开始")
    await asyncio.sleep(2)
    print(f"[{name}] 完成")

async def main():
    # 方式1：create_task() - 创建任务但不等待
    task = asyncio.create_task(background_job("Task-1"))
    
    print("主程序继续执行，不阻塞")
    await asyncio.sleep(0.5)
    print("做其他事情")
    
    # 如果需要，可以等待
    await task  # 等待任务完成

asyncio.run(main())

# 输出顺序：
# [Task-1] 开始
# 主程序继续执行，不阻塞
# 做其他事情
# [Task-1] 完成
```

**对比：直接 await（会阻塞）**

```python
async def main():
    # ❌ 这样会阻塞，等待任务完成才继续
    await background_job("Task-1")
    print("主程序继续")  # 要等 2 秒才会执行
```

**实际应用**：FastAPI 后台任务

```python
@router.post("/batch")
async def batch_add_items(items_data: list[ItemCreate]):
    # 创建后台任务，立即返回响应
    asyncio.create_task(create_items_batch_background(items_data))
    
    # 立即返回（不等待任务完成）
    return MessageResponse(message="已接受数据，正在后台处理")
```

---

### 2.2 并发运行多个任务 - gather()

**场景**：需要运行多个任务，并等待全部完成

```python
import asyncio

async def task_a():
    print("A 开始")
    await asyncio.sleep(2)
    print("A 完成")
    return "结果A"

async def task_b():
    print("B 开始")
    await asyncio.sleep(3)
    print("B 完成")
    return "结果B"

async def task_c():
    print("C 开始")
    await asyncio.sleep(1)
    print("C 完成")
    return "结果C"

async def main():
    # gather() 并发运行多个任务，等待全部完成
    results = await asyncio.gather(
        task_a(),
        task_b(),
        task_c(),
    )
    print(results)  # ['结果A', '结果B', '结果C']

asyncio.run(main())

# 输出：
# A 开始
# B 开始
# C 开始
# C 完成  （1秒）
# A 完成  （2秒）
# B 完成  （3秒）
# ['结果A', '结果B', '结果C']
# 总耗时：3秒（如果是顺序执行需要 6秒）
```

**处理异常**

```python
async def main():
    results = await asyncio.gather(
        task_a(),
        task_b(),
        task_c(),
        return_exceptions=True  # 不中断，继续执行其他任务
    )
    print(results)
```

**实际应用**：批量查询多个数据库

```python
async def query_db(db_name, query):
    """查询数据库"""
    await asyncio.sleep(0.5)  # 模拟查询耗时
    return f"{db_name}: {query}"

async def main():
    # 并发查询 3 个数据库
    results = await asyncio.gather(
        query_db("db1", "SELECT * FROM users"),
        query_db("db2", "SELECT * FROM orders"),
        query_db("db3", "SELECT * FROM products"),
    )
    print(results)  # 总耗时 0.5s（不是 1.5s）
```

---

### 2.3 等待任意一个任务完成 - wait() 和 as_completed()

#### 2.3.1 asyncio.wait() - 更细粒度的控制

```python
import asyncio

async def task(name, delay):
    await asyncio.sleep(delay)
    return f"{name} done"

async def main():
    tasks = [
        asyncio.create_task(task("A", 2)),
        asyncio.create_task(task("B", 1)),
        asyncio.create_task(task("C", 3)),
    ]
    
    # 方式1：等待全部完成
    done, pending = await asyncio.wait(tasks)
    for task in done:
        print(task.result())
    
    # 方式2：等待第一个完成
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    print(f"第一个完成: {done.pop().result()}")
    print(f"还有 {len(pending)} 个任务在运行")
    
    # 等待其余任务完成
    done, pending = await asyncio.wait(pending)

asyncio.run(main())
```

#### 2.3.2 asyncio.as_completed() - 按完成顺序处理

```python
async def main():
    tasks = [
        asyncio.create_task(task("A", 2)),
        asyncio.create_task(task("B", 1)),
        asyncio.create_task(task("C", 3)),
    ]
    
    # 按完成顺序处理结果
    for future in asyncio.as_completed(tasks):
        result = await future
        print(f"任务完成: {result}")

# 输出：
# 任务完成: B done  (1s)
# 任务完成: A done  (2s)
# 任务完成: C done  (3s)
```

**实际应用**：爬虫（优先处理快速响应的请求）

```python
async def fetch(url):
    await asyncio.sleep(...)  # 网络请求
    return data

async def main():
    urls = ["url1", "url2", "url3", ...]
    tasks = [asyncio.create_task(fetch(url)) for url in urls]
    
    # 按完成顺序处理，优先获得快速响应
    for future in asyncio.as_completed(tasks):
        result = await future
        process(result)  # 立即处理
```

---

### 2.4 设置超时 - timeout()

**场景**：限制任务的执行时间

```python
import asyncio

async def slow_task():
    await asyncio.sleep(5)
    return "完成"

async def main():
    try:
        # 设置 2 秒超时
        result = await asyncio.wait_for(slow_task(), timeout=2)
    except asyncio.TimeoutError:
        print("任务超时！")  # 2秒后执行这里

asyncio.run(main())
```

**超时后取消任务**

```python
async def main():
    try:
        result = await asyncio.wait_for(slow_task(), timeout=2)
    except asyncio.TimeoutError:
        print("超时，任务被自动取消")
        # 任务自动被 cancel，不需要手动清理
```

**实际应用**：API 调用超时

```python
@router.get("/data")
async def get_data():
    try:
        data = await asyncio.wait_for(
            fetch_from_api(),
            timeout=5  # 5 秒超时
        )
        return data
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="API 超时")
```

---

### 2.5 任务取消 - cancel()

**场景**：需要中断正在运行的任务

```python
import asyncio

async def long_running_task():
    try:
        for i in range(10):
            print(f"工作中... {i}")
            await asyncio.sleep(1)
        return "完成"
    except asyncio.CancelledError:
        print("任务被取消")
        # 可以做清理工作
        raise

async def main():
    task = asyncio.create_task(long_running_task())
    
    await asyncio.sleep(3)  # 让任务运行 3 秒
    
    # 取消任务
    task.cancel()
    
    try:
        await task
    except asyncio.CancelledError:
        print("捕获到取消异常")

asyncio.run(main())

# 输出：
# 工作中... 0
# 工作中... 1
# 工作中... 2
# 任务被取消
# 捕获到取消异常
```

---

### 2.6 任务队列 - Queue()

**场景**：生产者-消费者模式

```python
import asyncio

async def producer(queue):
    """生产者：生成数据"""
    for i in range(5):
        print(f"生产: {i}")
        await queue.put(i)  # 放入队列
        await asyncio.sleep(0.5)
    await queue.put(None)  # 信号：生产完成

async def consumer(queue):
    """消费者：消费数据"""
    while True:
        item = await queue.get()  # 从队列取出
        if item is None:  # 检查完成信号
            break
        print(f"消费: {item}")
        await queue.task_done()

async def main():
    queue = asyncio.Queue()
    
    # 并发运行生产者和消费者
    await asyncio.gather(
        producer(queue),
        consumer(queue),
    )

asyncio.run(main())

# 输出：
# 生产: 0
# 消费: 0
# 生产: 1
# 消费: 1
# ...
```

**实际应用**：任务队列处理

```python
async def process_items(queue):
    """从队列处理任务"""
    while True:
        item = await queue.get()
        if item is None:
            break
        # 处理任务
        await handle_item(item)
        queue.task_done()

# 在 API 中使用
@router.post("/queue-task")
async def queue_task(item: ItemData):
    # 将任务加入队列
    await task_queue.put(item)
    return {"message": "任务已入队"}
```

---

### 2.7 事件 - Event()

**场景**：线程/任务间同步

```python
import asyncio

async def waiter(event, name):
    """等待事件"""
    print(f"{name} 等待中...")
    await event.wait()
    print(f"{name} 收到信号！")

async def setter(event):
    """设置事件"""
    await asyncio.sleep(2)
    print("设置事件")
    event.set()

async def main():
    event = asyncio.Event()
    
    await asyncio.gather(
        waiter(event, "Task-1"),
        waiter(event, "Task-2"),
        setter(event),
    )

asyncio.run(main())

# 输出：
# Task-1 等待中...
# Task-2 等待中...
# （2秒后）
# 设置事件
# Task-1 收到信号！
# Task-2 收到信号！
```

---

### 2.8 锁 - Lock()

**场景**：保护共享资源（防止竞态条件）

```python
import asyncio

class Counter:
    def __init__(self):
        self.value = 0
        self.lock = asyncio.Lock()
    
    async def increment(self):
        # 获取锁
        async with self.lock:
            # 临界区：只有一个任务能进来
            old_value = self.value
            await asyncio.sleep(0.01)  # 模拟耗时操作
            self.value = old_value + 1

async def main():
    counter = Counter()
    
    # 并发 10 个任务
    await asyncio.gather(*[
        counter.increment() for _ in range(10)
    ])
    
    print(counter.value)  # 10（正确）
    # 如果没有锁，可能是 1-9 的随机值（竞态条件）

asyncio.run(main())
```

---

## 3️⃣ 高级应用

### 3.1 协程包装函数（run_in_executor）

**场景**：在异步代码中调用同步函数

```python
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

def sync_function(name):
    """同步函数（会阻塞）"""
    time.sleep(2)
    return f"Hello {name}"

async def main():
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor()
    
    # 在线程池中运行同步函数
    result = await loop.run_in_executor(
        executor,
        sync_function,
        "World"
    )
    print(result)

asyncio.run(main())
```

**实际应用**：CPU 密集操作

```python
@router.get("/calculate")
async def calculate():
    loop = asyncio.get_event_loop()
    
    # 在线程池中执行 CPU 密集操作
    result = await loop.run_in_executor(
        None,
        expensive_calculation,
    )
    return {"result": result}
```

---

### 3.2 上下文管理器（asynccontextmanager）

```python
import asyncio
from contextlib import asynccontextmanager

@asynccontextmanager
async def database_session():
    """异步数据库会话"""
    print("连接数据库")
    session = await connect()
    try:
        yield session
    finally:
        print("关闭连接")
        await session.close()

async def main():
    async with database_session() as session:
        await session.query()

asyncio.run(main())
```

---

## 4️⃣ FastAPI 中的异步应用

### 4.1 后台任务（推荐）

```python
from fastapi import FastAPI, BackgroundTasks

app = FastAPI()

def send_email(email: str):
    """发送邮件"""
    time.sleep(5)  # 模拟发邮件

@app.post("/send")
async def send_notification(email: str, bg_tasks: BackgroundTasks):
    # 添加后台任务
    bg_tasks.add_task(send_email, email)
    # 立即返回
    return {"message": "邮件已排队"}
```

### 4.2 异步路由

```python
@app.get("/data")
async def get_data():
    # 并发查询多个源
    results = await asyncio.gather(
        fetch_from_db(),
        fetch_from_api(),
        fetch_from_cache(),
    )
    return results
```

### 4.3 后台任务 + create_task

```python
@app.post("/batch")
async def batch_operation(items: list[Item]):
    # 创建后台任务（无需等待）
    asyncio.create_task(process_items_background(items))
    
    # 立即返回
    return {"message": "已接受"}

async def process_items_background(items):
    # 使用独立会话处理
    async with db_manager.get_session_factory()() as session:
        await item_crud.create_many(db=session, objects=items)
```

---

## 5️⃣ 常见错误和最佳实践

### 5.1 常见错误

```python
# ❌ 错误1：忘记 await
async def main():
    result = fetch_data()  # 返回 coroutine，没有执行

# ✅ 正确
async def main():
    result = await fetch_data()  # 执行协程

# ❌ 错误2：在非异步函数中使用 await
def sync_function():
    result = await fetch_data()  # SyntaxError

# ✅ 正确
async def async_function():
    result = await fetch_data()

# ❌ 错误3：create_task 前没有事件循环
asyncio.create_task(task())  # RuntimeError

# ✅ 正确：在 async 函数内使用
async def main():
    asyncio.create_task(task())
```

### 5.2 最佳实践

```python
# ✅ 1. 总是使用 asyncio.run()（Python 3.7+）
asyncio.run(main())

# ✅ 2. 为后台任务添加异常处理
async def safe_background_task(data):
    try:
        await process(data)
    except Exception as e:
        print(f"错误: {e}")

# ✅ 3. 使用独立会话（数据库）
async def background_db_task():
    async with db_manager.get_session_factory()() as session:
        await crud.create_many(db=session, objects=data)

# ✅ 4. 设置合理的超时
try:
    await asyncio.wait_for(task(), timeout=5)
except asyncio.TimeoutError:
    print("超时")

# ✅ 5. 明确日志记录
print(f"[后台任务] 开始处理 {len(items)} 条记录")
print(f"[后台任务] 完成")
```

---

## 📚 总结表

| 用法 | 说明 | 场景 |
|------|------|------|
| `await` | 等待协程完成 | 需要获得结果 |
| `create_task()` | 创建后台任务 | 不需要等待结果 |
| `gather()` | 并发多个任务 | 需要所有结果 |
| `wait()` | 等待任务完成 | 需要细粒度控制 |
| `as_completed()` | 按完成顺序处理 | 流式处理结果 |
| `wait_for()` | 设置超时 | 防止无限等待 |
| `cancel()` | 取消任务 | 中断任务 |
| `Queue()` | 任务队列 | 生产者-消费者 |
| `Event()` | 事件同步 | 任务协调 |
| `Lock()` | 互斥锁 | 保护共享资源 |

---

## 🎯 你的项目中的应用

在你的 FastAPI 项目中：

```python
# 后台异步批量插入
@router.post("/batch")
async def batch_add_items(items_data: list[ItemCreate]):
    # 1. 创建后台任务（不等待）
    asyncio.create_task(create_items_batch_background(items_data))
    
    # 2. 其他快速操作
    await batch_add_items_2()
    
    # 3. 立即返回（总耗时 < 20ms）
    return MessageResponse(message="已接受，后台处理中")

# 后台处理函数：创建独立会话
async def create_items_batch_background(items_data):
    session_factory = db_manager.get_session_factory()
    async with session_factory() as session:
        try:
            await item_crud.create_many(db=session, objects=items_data)
            print(f"[后台任务] 成功创建 {len(items_data)} 条记录")
        except Exception as e:
            print(f"[后台任务] 创建失败: {e}")
```

这样既能：
- ⚡ 给客户端快速响应（< 20ms）
- 🔄 在后台执行耗时操作（100ms）
- 🔐 避免数据库会话冲突
- 📊 支持高并发（不阻塞主线程）

