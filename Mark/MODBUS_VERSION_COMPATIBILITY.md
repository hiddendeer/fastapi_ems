# Modbus 模拟器版本兼容性说明

## 📦 pymodbus 版本变化

### pymodbus 3.x（当前支持）✅

**主要变化：**
1. 移除了 `ModbusSlaveContext`
2. 引入了 `ModbusSimulatorContext`
3. API 调用方式改变

**导入方式：**

```python
# ✅ pymodbus 3.x 正确导入
from pymodbus.datastore import ModbusSimulatorContext

# 创建上下文
context = ModbusSimulatorContext()

# 设置值（从站ID, 功能码, 地址, 值列表）
context.setValues(1, 3, 0, [0x43DC, 0x4000])

# 读取值（从站ID, 功能码, 地址, 数量）
values = context.getValues(1, 3, 0, 2)
```

---

### pymodbus 2.x（不支持）❌

**旧的导入方式：**

```python
# ❌ pymodbus 2.x（已废弃）
from pymodbus.datastore import (
    ModbusSlaveContext,
    ModbusServerContext,
    ModbusSequentialDataBlock,
)

# 创建数据块
store = ModbusSlaveContext(
    hr=ModbusSequentialDataBlock(0, [0] * 100),
)

# 创建上下文
context = ModbusServerContext(slaves={1: store}, single=False)
```

---

## 🔧 错误解决方案

### 错误 1: ImportError: cannot import name 'ModbusSlaveContext'

**错误信息：**
```
ImportError: cannot import name 'ModbusSlaveContext' from 'pymodbus.datastore'
```

**原因：**
- pymodbus 3.x 移除了 `ModbusSlaveContext`

**解决方案：**
```bash
# 确保使用 pymodbus 3.x
pip install pymodbus>=3.5.0 --upgrade
```

---

### 错误 2: 连接失败

**错误信息：**
```
[WinError 1225] 远程计算机拒绝网络连接
```

**原因：**
- 没有 Modbus 服务器在运行

**解决方案：**
1. 使用模拟器测试（示例 3）
2. 或确保真实设备已启动

---

## 📊 版本对比表

| 功能 | pymodbus 2.x | pymodbus 3.x |
|------|-------------|-------------|
| 数据存储类 | `ModbusSlaveContext` | `ModbusSimulatorContext` |
| 服务器启动 | `StartTcpServer` | `StartAsyncTcpServer` |
| 异步支持 | 部分支持 | 完全支持 |
| API 风格 | 回调式 | async/await |
| 推荐使用 | ❌ | ✅ |

---

## 🚀 升级指南

### 从 pymodbus 2.x 升级到 3.x

**步骤 1: 卸载旧版本**
```bash
pip uninstall pymodbus
```

**步骤 2: 安装新版本**
```bash
pip install pymodbus>=3.5.0
```

**步骤 3: 更新代码**

**旧代码（2.x）：**
```python
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext

store = ModbusSlaveContext(hr=ModbusSequentialDataBlock(0, [0] * 100))
context = ModbusServerContext(slaves={1: store}, single=False)
```

**新代码（3.x）：**
```python
from pymodbus.datastore import ModbusSimulatorContext

context = ModbusSimulatorContext()
context.setValues(1, 3, 0, [0, 0])  # 从站1, 功能码3, 地址0
```

---

## 🔍 检查当前版本

```bash
# 方法 1: Python 命令
python -c "import pymodbus; print(pymodbus.__version__)"

# 方法 2: pip 命令
pip show pymodbus
```

**输出示例：**
```
3.11.4  # ✅ 支持
2.5.3   # ❌ 不支持
```

---

## 📝 API 变化详解

### 1. 数据存储初始化

**2.x 方式：**
```python
from pymodbus.datastore import ModbusSlaveContext, ModbusSequentialDataBlock

store = ModbusSlaveContext(
    di=ModbusSequentialDataBlock(0, [0] * 100),  # 离散输入
    co=ModbusSequentialDataBlock(0, [0] * 100),  # 线圈
    hr=ModbusSequentialDataBlock(0, [0] * 100),  # 保持寄存器
    ir=ModbusSequentialDataBlock(0, [0] * 100),  # 输入寄存器
)
```

**3.x 方式：**
```python
from pymodbus.datastore import ModbusSimulatorContext

# 自动创建所有数据块
context = ModbusSimulatorContext()
```

### 2. 设置寄存器值

**2.x 方式：**
```python
# 功能码, 地址, 值列表
store.setValues(3, 0, [0x43DC, 0x4000])
```

**3.x 方式：**
```python
# 从站ID, 功能码, 地址, 值列表
context.setValues(1, 3, 0, [0x43DC, 0x4000])
```

### 3. 读取寄存器值

**2.x 方式：**
```python
# 功能码, 地址, 数量
values = store.getValues(3, 0, 2)
```

**3.x 方式：**
```python
# 从站ID, 功能码, 地址, 数量
values = context.getValues(1, 3, 0, 2)
```

### 4. 服务器启动

**2.x 方式：**
```python
from pymodbus.server.sync import StartTcpServer

StartTcpServer(context, address=("127.0.0.1", 502))
```

**3.x 方式：**
```python
from pymodbus.server import StartAsyncTcpServer

await StartAsyncTcpServer(context=context, address=("127.0.0.1", 502))
```

---

## 🎯 推荐配置

### 生产环境

```bash
# 稳定版本
pip install pymodbus==3.5.0
```

### 开发环境

```bash
# 最新版本
pip install pymodbus>=3.11.0
```

### 测试环境

```bash
# 与生产环境保持一致
pip install pymodbus==3.5.0
```

---

## 📚 参考资源

- [pymodbus 官方文档](https://pymodbus.readthedocs.io/)
- [pymodbus GitHub](https://github.com/pymodbus-dev/pymodbus)
- [迁移指南](https://pymodbus.readthedocs.io/en/latest/source/migration.html)

---

**更新日期：** 2025-12-25  
**当前支持版本：** pymodbus 3.5.0+

