# IEC 61850 MMS 仿真代码阅读指南

本目录（`src/iecApi`）包含了一套精简的 IEC 61850 MMS 协议模拟实现。它使用纯 Python 模拟了 IED（服务端）的模型结构、客户端的请求逻辑以及核心的报告（Report）分发机制。

## 1. 文件功能概览

这三个文件构成了一个完整的“生产-消费”闭环：

| 文件名 | 角色 | 核心逻辑 |
| :--- | :--- | :--- |
| **`model.py`** | **服务端 (Server)** | 定义了 IEC 61850 的树状模型（LD/LN/DO/DA）以及数据变化触发机制。 |
| **`client.py`** | **客户端 (Client)** | 模拟 SCADA 或后台系统，实现读取、目录浏览及订阅报告的功能。 |
| **`demo.py`** | **演示脚本 (Orchestrator)** | 组装并运行整个流程，展示从上电、连接、发现到数据变更触发报告的全过程。 |

---

## 2. 推荐阅读顺序

建议按照以下顺序深入理解：

### 第一步：`model.py` (理解骨架)
**重点关注：**
*   **对象层级：** 注意 `IecServer` -> `LogicalDevice` -> `LogicalNode` -> `DataObject` -> `DataAttribute` 的嵌套关系。这是 61850 建模的核心。
*   **触发机制：** 关注 `DataAttribute.value` 的 setter 方法（第 25-36 行）。这是整个仿真的“灵魂”——当属性值改变时，它如何通知所有监听它的报告控制块（RCB）。
*   **RCB 逻辑：** `ReportControlBlock` 类，看它如何维护数据集（Dataset）并在数据变动时拼装报告。

### 第二步：`client.py` (理解交互)
**重点关注：**
*   **连接模型：** `connect` 方法简单地将 Server 对象引用给 Client，模拟 TCP 握手。
*   **发现与读取：** `get_server_directory` 展示了如何递归遍历树状模型；`read_value` 展示了根据路径（Path）寻址的过程。
*   **异步报告接收：** 观察 `_on_report_received` 及其注册到 RCB 的过程。这模拟了 MMS 服务器如何主动向客户端推送到来的 TCP 包。

### 第三步：`demo.py` (看运行效果)
**重点关注：**
*   **建模过程：** `build_mock_server` 函数。这相当于 IED 的工程配置（对应实际项目中的 SCL/SCD 文件配置）。
*   **全流程执行：** `run_demo` 中的步骤 1 到 步骤 6。
*   **硬件触发模拟：** 倒数第 10 行附近的 `voltage_sensor_a.value = new_voltage`。这行代码模拟了传感器检测到电压变化，然后观察它如何一路触发直到客户端打印出报告。

---

## 3. 核心概念对应表

如果你正在学习 IEC 61850，可以在代码中寻找以下概念的对应实现：

| IEC 61850 术语 | 代码实现位置 | 说明 |
| :--- | :--- | :--- |
| **MMS** | `client.py` / `model.py` | 模拟了 Read/GetDirectory/Report 等 MMS 服务。 |
| **LD / LN / DO / DA** | `model.py` 中的同名类 | 构成了数据建模的四个层级。 |
| **DataSet (数据集)** | `LogicalNode.create_dataset` | 实现将多个数据项打包在一起的功能。 |
| **RCB (报告控制块)** | `ReportControlBlock` 类 | 负责监控数据集并决定何时发送消息。 |
| **dchg (Data Change)** | `reason="dchg"` (在 `model.py` 第 177 行) | 报告触发的原因，表示因为数据改变产生的报告。 |

---

## 4. 如何运行

在项目根目录下，执行以下命令即可看到仿真效果：

```bash
python src/iecApi/demo.py
```

**观察重点：**
运行后请留意控制台输出，特别是带 `⚡⚡` 符号的部分，那是客户端**异步收到的报告**，而不是通过读取得到的。

---

## 5. 学习建议
1.  **魔改参数**：尝试在 `demo.py` 中添加一个新的 `DataObject`（比如开关位置 `Pos`），并修改代码让它也能触发报告。
2.  **断点调试**：在 `DataAttribute.value` 的 setter 处打断点，观察当你在 `demo.py` 修改值时，调用栈是如何一步步跳转到 `ReportControlBlock` 再到 `IecClient` 的。
