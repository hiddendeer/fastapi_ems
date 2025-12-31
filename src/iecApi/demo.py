import time
# 尝试相对导入 (当作为包运行 / python -m src.iecApi.demo 时)
# 如果失败 (ImportError / 作为脚本直接运行 python demo.py)，则回退到绝对导入
try:
    from .model import IecServer, LogicalDevice, LogicalNode, DataObject
    from .client import IecClient
except ImportError:
    from model import IecServer, LogicalDevice, LogicalNode, DataObject
    from client import IecClient

def build_mock_server():
    """
    搭建一个虚拟的 IED (智能电子设备)
    模型结构: MyIED (服务端) / Protection (逻辑设备) / MMXU1 (测量逻辑节点)
    """
    server = IecServer("MySubstation_IED_001")
    
    # 1. 创建 Logical Device (LD: 逻辑设备), 例如: "Protection" (保护分区)
    ld = server.add_ld("Protection")
    
    # 2. 创建 Logical Node (LN: 逻辑节点), 例如: "MMXU1" (测量单元)
    ln_mmxu = ld.add_ln("MMXU1")
    
    # 3. 创建 Data Objects (DO: 数据对象), 例如: "PhV" (Phase Voltage - 相电压)
    do_phv = ln_mmxu.add_do("PhV")
    
    # 4. 创建 Data Attributes (DA: 数据属性)
    # 路径: mag.f (Magnitude Float - 浮点幅值)
    da_ids = []
    # A相电压
    da_a = do_phv.add_da("phsA.cVal.mag.f", 220.0) 
    da_ids.append(da_a)
    # B相电压
    da_b = do_phv.add_da("phsB.cVal.mag.f", 219.5)
    da_ids.append(da_b)
    
    # 5. 配置报告 (Dataset & RCB)
    # 定义一个数据集 "dsMeas" (购物车), 里面包含 A相和 B相电压
    ln_mmxu.create_dataset("dsMeas", da_ids)
    
    # 基于该数据集创建一个报告控制块 (RCB: 快递单)
    # 名字: "urcb01", 报告ID: "MyIED/Protection/MMXU1$RP$urcb01"
    ln_mmxu.create_report("urcb01", "dsMeas", "MyIED/Protection/MMXU1$RP$urcb01")
    
    return server, da_a # 返回 server 以及一个具体的属性对象(用于后续模拟修改值)

def run_demo():
    print("=== IEC 61850 MMS 仿真演示 (纯Python模拟) ===\n")

    # 步骤 1: 启动 Server (模拟物理装置上电)
    print("--- [步骤 1] 启动服务端 (IED) ---")
    my_server, voltage_sensor_a = build_mock_server()
    print("服务端已就绪 (虚拟监听端口 102...)\n")

    # 步骤 2: 启动 Client (模拟 SCADA/监控后台)
    print("--- [步骤 2] 启动客户端 (SCADA) ---")
    client = IecClient()
    
    # 建立连接
    client.connect(my_server)
    
    # 步骤 3: 模型发现 (Discovery)
    # 相当于客户端询问: "你有哪些数据?"
    client.get_server_directory()

    # 步骤 4: 主动读取 (Polling)
    # 传统的“一问一答”模式
    print("--- [步骤 3] 主动轮询 (客户端请求数据) ---")
    val = client.read_value("Protection/MMXU1.PhV.phsA.cVal.mag.f")
    
    # 步骤 5: 启用报告 (Reporting)
    # 现代的“订阅-推送”模式
    print("\n--- [步骤 4] 配置报告订阅 (Subscribe) ---")
    # 客户端告诉服务端: "如果 'urcb01' 关联的数据变了，请发报告给我"
    client.enable_report("Protection", "MMXU1", "urcb01")

    # 步骤 6: 模拟硬件层数据变化
    print("\n--- [步骤 5] 模拟物理环境变化 (电压波动) ---")
    print("(等待电压波动...)")
    time.sleep(1)
    
    # 在服务端直接修改底层数据 (模拟传感器采集到了新数值)
    # 根据 IEC 61850 机制，这应该会自动触发报告推送
    new_voltage = 225.5
    print(f"\n[硬件层] 传感器检测到电压变为: {new_voltage}!")
    voltage_sensor_a.value = new_voltage
    
    # 等待一小会儿，确保看到异步打印的报告
    time.sleep(1)
    
    print("\n=== 演示结束 ===")

if __name__ == "__main__":
    run_demo()
