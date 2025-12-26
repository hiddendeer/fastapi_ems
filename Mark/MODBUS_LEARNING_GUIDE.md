# Modbus 异步通信学习指南

## 📚 学习目标

通过本示例代码，你将学习到：

1. ✅ **Modbus 协议基础**
   - 保持寄存器（Holding Registers）的读写
   - 功能码 0x03（读）和 0x10（写）
   - 从站 ID（Slave ID）和寄存器地址

2. ✅ **Python 异步编程**
   - `async/await` 语法
   - `asyncio` 事件循环
   - 并发任务管理

3. ✅ **多设备并发采集**
   - 同时管理多个设备
   - 异步并发提高效率
   - 任务调度和协调

4. ✅ **异常处理和重连机制**
   - 连接失败自动重试
   - 断线自动重连
   - 异常捕获和恢复

5. ✅ **数据转换**
   - 浮点数与寄存器的转换
   - 大端序（Big-Endian）数据处理
   - `struct` 模块使用

## 🚀 快速开始

### 1. 安装依赖

```bash
# 进入 pyModbus 目录
cd pyModbus

# 安装依赖包
pip install -r requirements.txt
```

### 2. 运行示例

```bash
# 运行 Modbus 模拟器
python sim_modbus.py
```

## 📖 代码结构详解

### 核心类说明

```
sim_modbus.py
├── ModbusConfig          # 配置类：定义连接参数和寄存器地址
├── ModbusClient          # 客户端类：封装连接、读写、重连
├── DataConverter         # 转换类：浮点数与寄存器互转
├── DeviceCollector       # 采集器类：单设备数据采集
├── MultiDeviceManager    # 管理器类：多设备并发管理
└── ModbusSimulator       # 模拟器类：用于测试
```

### 1. ModbusConfig - 配置类

**作用：** 定义设备连接参数和寄存器地址映射

```python
config = ModbusConfig(
    host="192.168.1.100",  # Modbus 服务器 IP
    port=502,              # Modbus TCP 端口（标准端口）
    slave_id=1,            # 从站 ID（设备地址）
    timeout=3,             # 连接超时时间（秒）
    retry_times=3,         # 重试次数
    retry_delay=1.0,       # 重试延迟（秒）
)
```

**寄存器地址映射：**

| 参数 | 寄存器地址 | 数据类型 | 说明 |
|------|-----------|---------|------|
| 电压 | 0x0000 (0) | Float32 | 占用 2 个寄存器 |
| 电流 | 0x0002 (2) | Float32 | 占用 2 个寄存器 |
| 功率 | 0x0004 (4) | Float32 | 占用 2 个寄存器 |

### 2. ModbusClient - 客户端类

**作用：** 封装 Modbus TCP 客户端，处理连接、读写、重连

**核心方法：**

#### 2.1 连接管理

```python
# 建立连接
await client.connect()

# 确保连接（自动重连）
await client.ensure_connected()

# 断开连接
await client.disconnect()
```

#### 2.2 读取保持寄存器

```python
# 读取 2 个寄存器（从地址 0 开始）
registers = await client.read_holding_registers(
    address=0,  # 起始地址
    count=2,    # 读取数量
)

# 返回值: [高位寄存器, 低位寄存器]
# 例如: [0x43DC, 0x0000] 表示 220.0
```

**Modbus 功能码：** 0x03（读保持寄存器）

#### 2.3 写入保持寄存器

```python
# 写入 2 个寄存器
success = await client.write_holding_registers(
    address=0,        # 起始地址
    values=[0x43DC, 0x0000],  # 寄存器值
)
```

**Modbus 功能码：** 0x10（写多个保持寄存器）

### 3. DataConverter - 数据转换类

**作用：** 处理浮点数与 Modbus 寄存器之间的转换

#### 3.1 浮点数转寄存器

```python
# 将 220.5 转换为 2 个寄存器
registers = DataConverter.float_to_registers(220.5)
# 返回: [0x43DC, 0x4000]
```

**转换过程：**

```
220.5 (float)
  ↓ struct.pack('>f', 220.5)
0x43DC4000 (4 字节)
  ↓ struct.unpack('>HH', bytes)
[0x43DC, 0x4000] (2 个寄存器)
```

#### 3.2 寄存器转浮点数

```python
# 将 2 个寄存器转换为浮点数
value = DataConverter.registers_to_float([0x43DC, 0x4000])
# 返回: 220.5
```

**关键点：**
- 使用 **大端序（Big-Endian）** 格式
- 32 位浮点数占用 **2 个 16 位寄存器**
- 高位寄存器在前，低位寄存器在后

### 4. DeviceCollector - 设备采集器

**作用：** 负责单个设备的数据采集

#### 4.1 读取单个参数

```python
collector = DeviceCollector("设备1", client)

# 读取电压
voltage = await collector.read_voltage()

# 读取电流
current = await collector.read_current()

# 读取功率
power = await collector.read_power()
```

#### 4.2 读取所有参数

```python
# 并发读取所有参数（更高效）
data = await collector.read_all_data()
# 返回: {
#     "voltage": 220.5,
#     "current": 10.2,
#     "power": 2248.1
# }
```

#### 4.3 持续采集

```python
# 启动持续采集（每 1 秒采集一次）
await collector.start_collecting(interval=1.0)

# 停止采集
collector.stop_collecting()
```

### 5. MultiDeviceManager - 多设备管理器

**作用：** 管理多个设备的并发采集

```python
# 创建管理器
manager = MultiDeviceManager()

# 添加设备
manager.add_device("设备1", ModbusConfig(host="192.168.1.100", ...))
manager.add_device("设备2", ModbusConfig(host="192.168.1.101", ...))
manager.add_device("设备3", ModbusConfig(host="192.168.1.102", ...))

# 启动所有设备采集
await manager.start_all(interval=2.0)

# 停止所有设备
manager.stop_all()

# 断开所有连接
await manager.disconnect_all()
```

## 🔧 核心技术详解

### 1. 异步编程（Async/Await）

#### 1.1 为什么使用异步？

**同步方式的问题：**

```python
# 同步方式 - 阻塞式
def read_data():
    data1 = read_device1()  # 等待 1 秒
    data2 = read_device2()  # 等待 1 秒
    data3 = read_device3()  # 等待 1 秒
    # 总耗时: 3 秒
```

**异步方式的优势：**

```python
# 异步方式 - 并发执行
async def read_data():
    data1, data2, data3 = await asyncio.gather(
        read_device1(),  # 并发执行
        read_device2(),  # 并发执行
        read_device3(),  # 并发执行
    )
    # 总耗时: 1 秒（并发）
```

#### 1.2 async/await 语法

```python
# 定义异步函数
async def my_async_function():
    # await 等待异步操作完成
    result = await some_async_operation()
    return result

# 调用异步函数
result = await my_async_function()

# 或者使用 asyncio.run()
asyncio.run(my_async_function())
```

#### 1.3 并发任务

```python
# 方式 1: asyncio.gather（推荐）
results = await asyncio.gather(
    task1(),
    task2(),
    task3(),
)

# 方式 2: asyncio.create_task
task1 = asyncio.create_task(func1())
task2 = asyncio.create_task(func2())
await task1
await task2
```

### 2. 异常处理和重连机制

#### 2.1 连接失败重试

```python
async def ensure_connected(self) -> bool:
    # 如果已连接，直接返回
    if self.connected and self.client.connected:
        return True
    
    # 重试机制
    for attempt in range(self.config.retry_times):
        if await self.connect():
            return True
        
        # 等待后重试
        await asyncio.sleep(self.config.retry_delay)
    
    return False
```

#### 2.2 异常捕获

```python
try:
    # 尝试读取数据
    response = await self.client.read_holding_registers(...)
    
except ModbusException as e:
    # Modbus 协议异常
    print(f"Modbus 异常: {e}")
    self.connected = False  # 标记为断开
    
except Exception as e:
    # 其他异常
    print(f"未知异常: {e}")
    self.connected = False
```

#### 2.3 自动重连

```python
async with self.lock:  # 使用锁防止并发冲突
    # 每次操作前确保连接
    if not await self.ensure_connected():
        return None
    
    # 执行操作
    response = await self.client.read_holding_registers(...)
```

### 3. 粘包处理

**什么是粘包？**

TCP 是流式协议，多个数据包可能粘在一起接收。

**pymodbus 的处理方式：**

- ✅ pymodbus 内部已处理粘包问题
- ✅ 使用 MBAP 头（Modbus Application Protocol Header）
- ✅ 每个请求都有唯一的事务 ID

**MBAP 头结构：**

```
| 事务ID(2字节) | 协议ID(2字节) | 长度(2字节) | 单元ID(1字节) | 功能码(1字节) | 数据 |
```

### 4. 并发控制（锁机制）

```python
# 创建异步锁
self.lock = asyncio.Lock()

# 使用锁保护临界区
async with self.lock:
    # 同一时间只有一个协程可以执行这里的代码
    response = await self.client.read_holding_registers(...)
```

**为什么需要锁？**

- 防止多个协程同时操作同一个连接
- 避免数据混乱
- 保证操作的原子性

## 📊 实际应用场景

### 场景 1: 电力监控系统

```python
# 监控多个电表
manager = MultiDeviceManager()

# 添加 10 个电表
for i in range(1, 11):
    manager.add_device(
        f"电表{i}",
        ModbusConfig(host=f"192.168.1.{100+i}", port=502, slave_id=1)
    )

# 每 5 秒采集一次
await manager.start_all(interval=5.0)
```

### 场景 2: 工业设备监控

```python
# 监控生产线设备
devices = [
    ("压力传感器", "192.168.1.10"),
    ("温度传感器", "192.168.1.11"),
    ("流量计", "192.168.1.12"),
]

manager = MultiDeviceManager()
for name, ip in devices:
    manager.add_device(name, ModbusConfig(host=ip, port=502))

await manager.start_all(interval=1.0)
```

### 场景 3: 数据采集和存储

```python
async def collect_and_save():
    collector = DeviceCollector("设备1", client)
    
    while True:
        # 采集数据
        data = await collector.read_all_data()
        
        # 保存到数据库
        await save_to_database(data)
        
        # 等待下次采集
        await asyncio.sleep(10)
```

## 🐛 常见问题和解决方案

### 问题 1: 连接超时

**原因：**
- 网络不通
- 设备未启动
- IP 地址错误
- 防火墙阻止

**解决方案：**

```python
# 增加超时时间和重试次数
config = ModbusConfig(
    host="192.168.1.100",
    timeout=10,  # 增加到 10 秒
    retry_times=5,  # 增加到 5 次
    retry_delay=2.0,  # 延迟 2 秒
)
```

### 问题 2: 读取数据错误

**原因：**
- 寄存器地址错误
- 从站 ID 错误
- 数据格式不匹配

**解决方案：**

```python
# 1. 检查寄存器地址
config.registers = {
    "voltage": 0,  # 确认正确的地址
    "current": 2,
    "power": 4,
}

# 2. 检查从站 ID
config.slave_id = 1  # 确认设备的从站 ID

# 3. 检查数据格式
# 如果设备使用小端序，修改转换函数
packed = struct.pack('<f', value)  # 小端序
```

### 问题 3: 内存泄漏

**原因：**
- 连接未关闭
- 任务未取消

**解决方案：**

```python
try:
    await collector.start_collecting()
finally:
    # 确保清理资源
    collector.stop_collecting()
    await client.disconnect()
```

## 📝 学习建议

### 1. 循序渐进

1. **第一步：** 理解 Modbus 协议基础
   - 保持寄存器是什么
   - 功能码的作用
   - 寄存器地址映射

2. **第二步：** 掌握异步编程
   - `async/await` 语法
   - `asyncio.gather()` 并发
   - 异常处理

3. **第三步：** 实践单设备采集
   - 运行 `example_single_device()`
   - 修改参数观察效果
   - 添加日志输出

4. **第四步：** 实践多设备采集
   - 运行 `example_multi_device()`
   - 理解并发机制
   - 观察性能提升

### 2. 动手实验

```python
# 实验 1: 修改采集间隔
await collector.start_collecting(interval=0.5)  # 改为 0.5 秒

# 实验 2: 添加更多参数
config.registers["temperature"] = 6  # 添加温度寄存器

# 实验 3: 修改重连策略
config.retry_times = 10  # 增加重试次数
config.retry_delay = 0.5  # 减少延迟
```

### 3. 调试技巧

```python
# 1. 添加详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 2. 打印原始数据
print(f"原始寄存器: {registers}")
print(f"转换后数值: {value}")

# 3. 使用 try-except 捕获异常
try:
    data = await collector.read_all_data()
except Exception as e:
    print(f"异常详情: {e}")
    import traceback
    traceback.print_exc()
```

## 🔗 参考资源

### 官方文档

- [pymodbus 官方文档](https://pymodbus.readthedocs.io/)
- [Python asyncio 文档](https://docs.python.org/3/library/asyncio.html)
- [Modbus 协议规范](https://modbus.org/docs/Modbus_Application_Protocol_V1_1b3.pdf)

### 学习资源

- [Modbus 协议详解](https://www.modbustools.com/modbus.html)
- [Python 异步编程教程](https://realpython.com/async-io-python/)
- [struct 模块使用](https://docs.python.org/3/library/struct.html)

## 🎯 下一步学习

1. **集成到 FastAPI**
   - 创建 API 接口
   - 实时数据推送
   - WebSocket 通信

2. **数据存储**
   - 保存到数据库
   - 时序数据处理
   - 历史数据查询

3. **数据可视化**
   - 实时曲线图
   - 数据统计分析
   - 告警和通知

4. **高级功能**
   - 数据校验和过滤
   - 异常检测
   - 自动化控制

---

**祝你学习愉快！** 🎓

如有问题，请参考代码中的详细注释或查阅官方文档。

