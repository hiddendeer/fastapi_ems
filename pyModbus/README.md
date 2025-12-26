# Modbus 模拟器使用说明

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装 pymodbus 3.x 版本（推荐 3.5.0 或更高）
pip install pymodbus>=3.5.0

# 或者指定具体版本
pip install pymodbus==3.11.4
```

**版本说明：**
- ✅ 支持 pymodbus 3.5.0 及以上版本
- ❌ 不支持 pymodbus 2.x（API 已变更）

### 2. 运行示例

```bash
python sim_modbus.py
```

## 📖 三种运行模式

### 模式 1: 使用模拟器测试（推荐新手）✅

**特点：** 自动启动 Modbus 服务器，无需外部设备

```python
# 在 main() 函数中
await example_with_simulator()
```

**流程：**
1. 启动 Modbus 模拟服务器（127.0.0.1:5020）
2. 模拟器自动生成电压、电流、功率数据
3. 客户端连接并采集数据
4. 采集 10 秒后自动停止

**适用场景：**
- ✅ 学习 Modbus 协议
- ✅ 测试代码功能
- ✅ 没有真实设备

---

### 模式 2: 单设备采集

**特点：** 连接真实的 Modbus 设备

```python
# 在 main() 函数中
await example_single_device()
```

**前提条件：**
- ⚠️ 需要有真实的 Modbus TCP 服务器运行
- ⚠️ 修改 IP 地址和端口为实际设备地址

**配置示例：**

```python
config = ModbusConfig(
    host="192.168.1.100",  # 修改为实际设备 IP
    port=502,              # 标准 Modbus 端口
    slave_id=1,            # 设备从站 ID
)
```

---

### 模式 3: 多设备并发采集

**特点：** 同时采集多个设备

```python
# 在 main() 函数中
await example_multi_device()
```

**前提条件：**
- ⚠️ 需要多个真实的 Modbus 设备
- ⚠️ 修改每个设备的 IP 地址

**配置示例：**

```python
manager.add_device("设备1", ModbusConfig(host="192.168.1.100", port=502))
manager.add_device("设备2", ModbusConfig(host="192.168.1.101", port=502))
manager.add_device("设备3", ModbusConfig(host="192.168.1.102", port=502))
```

---

## 🔧 常见问题

### Q1: 连接失败 "远程计算机拒绝网络连接"

**原因：** 没有 Modbus 服务器在运行

**解决方案：**
1. 使用模式 1（模拟器测试）
2. 或者确保真实设备已启动并可访问

---

### Q2: 如何修改端口号？

**修改配置类的默认端口：**

```python
class ModbusConfig:
    def __init__(
        self,
        host: str,
        port: int = 5020,  # 修改这里的默认值
        ...
    ):
```

**或者在创建配置时指定：**

```python
config = ModbusConfig(
    host="127.0.0.1",
    port=5020,  # 指定端口
)
```

---

### Q3: 如何修改采集间隔？

```python
# 每 0.5 秒采集一次
await collector.start_collecting(interval=0.5)

# 每 5 秒采集一次
await collector.start_collecting(interval=5.0)
```

---

### Q4: 如何添加更多寄存器？

**步骤 1：** 在配置类中添加寄存器地址

```python
self.registers = {
    "voltage": 0,
    "current": 2,
    "power": 4,
    "temperature": 6,  # 新增温度寄存器
}
```

**步骤 2：** 在采集器中添加读取方法

```python
async def read_temperature(self) -> Optional[float]:
    address = self.client.config.registers["temperature"]
    registers = await self.client.read_holding_registers(address, count=2)
    if registers is None:
        return None
    return DataConverter.registers_to_float(registers)
```

---

## 📊 输出示例

```
============================================================
🎓 Modbus 异步通信学习示例
============================================================

请选择示例:
1. 单设备采集
2. 多设备并发采集
3. 使用模拟器测试

============================================================
示例 3: 使用模拟器测试
============================================================

[2025-12-25 14:45:00] 🖥️ Modbus 模拟器启动: 127.0.0.1:5020
[2025-12-25 14:45:00] 🔄 开始模拟数据变化...
[2025-12-25 14:45:02] ⏳ 等待 Modbus 服务器启动...
[2025-12-25 14:45:02] ✅ 成功连接到 127.0.0.1:5020
[2025-12-25 14:45:02] 🚀 开始采集数据（10秒）...

[2025-12-25 14:45:02] 🚀 [测试设备] 开始采集数据...
[2025-12-25 14:45:02] 📊 [测试设备] 电压: 220.50V | 电流: 10.20A | 功率: 2248.10W
[2025-12-25 14:45:03] 📊 [测试设备] 电压: 221.20V | 电流: 10.50A | 功率: 2322.60W
[2025-12-25 14:45:04] 📊 [测试设备] 电压: 219.80V | 电流: 10.10A | 功率: 2219.98W
...
[2025-12-25 14:45:12] ⏰ 采集完成（10秒到）
[2025-12-25 14:45:12] 🧹 清理资源...
[2025-12-25 14:45:12] 🛑 [测试设备] 停止采集数据
[2025-12-25 14:45:12] 🔌 已断开连接: 127.0.0.1:5020
[2025-12-25 14:45:12] 🛑 Modbus 模拟器停止
[2025-12-25 14:45:12] ✅ 测试完成！
```

---

## 🎓 学习建议

1. **第一步：** 运行模式 1（模拟器测试），理解基本流程
2. **第二步：** 阅读代码注释，理解每个类的作用
3. **第三步：** 修改参数（采集间隔、重试次数等），观察效果
4. **第四步：** 尝试添加新的寄存器和读取方法
5. **第五步：** 连接真实设备（模式 2 或 3）

---

## 📚 相关文档

- [完整学习指南](../Mark/MODBUS_LEARNING_GUIDE.md)
- [pymodbus 官方文档](https://pymodbus.readthedocs.io/)
- [Modbus 协议规范](https://modbus.org/)

---

**祝你学习愉快！** 🎉

