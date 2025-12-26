"""
Modbus 模拟器与客户端 - 异步实现
功能：
1. 模拟 Modbus TCP 服务器（提供电压、电流、功率数据）
2. Modbus TCP 客户端（读取数据、断线重连）
3. 支持多设备并发采集
4. 结构化设计，支持长时间稳定运行

改进点：
- 优化代码结构，分离配置、客户端、服务器和业务逻辑
- 使用 logging 模块替代 print
- 支持优雅退出 (Graceful Shutdown)
- 默认无限运行，直到收到停止信号
"""

import asyncio
import logging
import random
import struct
from datetime import datetime
from typing import Dict, List, Optional, Any

# 第三方库导入
try:
    from pymodbus.client import AsyncModbusTcpClient
    from pymodbus.exceptions import ModbusException
    from pymodbus.pdu import ExceptionResponse
    # 服务器组件
    from pymodbus.server import StartAsyncTcpServer
    from pymodbus.datastore import (
        ModbusSequentialDataBlock,
        ModbusDeviceContext,
        ModbusServerContext,
    )
except ImportError as e:
    print(f"❌ 缺少必要依赖: {e}")
    print("请运行: pip install 'pymodbus>=3.5.0'")
    exit(1)

# ==================== 日志配置 ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("ModbusSim")

# ==================== 配置常量 ====================
class AppConfig:
    """全局应用配置"""
    HOST = "127.0.0.1"
    PORT = 5020
    SLAVE_ID = 1
    
    # 采集配置
    COLLECT_INTERVAL = 1.0  # 秒
    RETRY_TIMES = 3
    RETRY_DELAY = 1.0
    
    # 寄存器地址 (保持寄存器 Holding Registers)
    REG_VOLTAGE = 0  # 220V (占用 2 个寄存器)
    REG_CURRENT = 2  # 10A  (占用 2 个寄存器)
    REG_POWER = 4    # 2200W (占用 2 个寄存器)

# ==================== 工具类 ====================
class DataConverter:
    """数据转换工具：处理浮点数与寄存器(16位整数)之间的转换"""
    
    @staticmethod
    def float_to_registers(value: float) -> List[int]:
        """float (32位) -> 2 * uint16"""
        # '>f': Big-Endian float
        packed = struct.pack('>f', value)
        # '>HH': 2 * Big-Endian unsigned short
        return list(struct.unpack('>HH', packed))

    @staticmethod
    def registers_to_float(registers: List[int]) -> float:
        """2 * uint16 -> float (32位)"""
        if len(registers) < 2:
            raise ValueError("Need at least 2 registers for float")
        packed = struct.pack('>HH', registers[0], registers[1])
        return struct.unpack('>f', packed)[0]

# ==================== Modbus 客户端 ====================
class ModbusClientWrapper:
    """封装 pymodbus 客户端，处理连接和重连逻辑"""
    
    def __init__(self, host: str, port: int, slave_id: int):
        self.host = host
        self.port = port
        self.slave_id = slave_id
        self.client: Optional[AsyncModbusTcpClient] = None
        self._lock = asyncio.Lock()
        self._connected = False

    async def connect(self) -> bool:
        """建立连接"""
        try:
            if self.client is None:
                self.client = AsyncModbusTcpClient(
                    host=self.host,
                    port=self.port,
                    timeout=3.0
                )
            
            if not self.client.connected:
                await self.client.connect()
                
            if self.client.connected:
                self._connected = True
                logger.info(f"✅ 已连接到 Modbus 服务器 {self.host}:{self.port}")
                return True
            else:
                logger.warning(f"❌ 连接失败 {self.host}:{self.port}")
                return False
        except Exception as e:
            logger.error(f"❌ 连接异常: {e}")
            self._connected = False
            return False

    async def disconnect(self):
        """断开连接"""
        if self.client:
            self.client.close()
            self._connected = False
            logger.info("🔌 已断开连接")

    async def ensure_connected(self) -> bool:
        """确保连接可用，自动重连"""
        if self._connected and self.client and self.client.connected:
            return True
        
        logger.info("🔄 尝试重新连接...")
        for i in range(AppConfig.RETRY_TIMES):
            if await self.connect():
                return True
            await asyncio.sleep(AppConfig.RETRY_DELAY)
        
        return False

    async def read_float(self, address: int) -> Optional[float]:
        """读取浮点数 (跨越2个寄存器)"""
        async with self._lock:
            if not await self.ensure_connected():
                return None
            
            try:
                # read_holding_registers(address, count, slave)
                # pymodbus 3.x (newer versions) uses device_id instead of slave
                response = await self.client.read_holding_registers(
                    address=address,
                    count=2,
                    # slave=self.slave_id  # Old 3.x
                    device_id=self.slave_id  # New 3.11+
                )
                
                if response.isError():
                    logger.warning(f"⚠️ 读取错误 (Addr {address}): {response}")
                    return None
                
                if isinstance(response, ExceptionResponse):
                    logger.warning(f"⚠️ 异常响应 (Addr {address}): {response}")
                    return None

                return DataConverter.registers_to_float(response.registers)
                
            except ModbusException as e:
                logger.error(f"❌ Modbus 协议异常: {e}")
                self._connected = False # 标记断开，触发重连
                return None
            except Exception as e:
                logger.error(f"❌ 读取异常: {e}")
                return None

    async def write_float(self, address: int, value: float) -> bool:
        """写入浮点数"""
        async with self._lock:
            if not await self.ensure_connected():
                return False
            
            try:
                registers = DataConverter.float_to_registers(value)
                response = await self.client.write_registers(
                    address=address,
                    values=registers,
                    # slave=self.slave_id
                    device_id=self.slave_id
                )
                
                if response.isError() or isinstance(response, ExceptionResponse):
                    logger.warning(f"⚠️ 写入失败 (Addr {address})")
                    return False
                
                return True
            except Exception as e:
                logger.error(f"❌ 写入异常: {e}")
                self._connected = False
                return False

# ==================== 采集业务逻辑 ====================
class DeviceCollector:
    """设备数据采集器"""
    
    def __init__(self, name: str, client: ModbusClientWrapper):
        self.name = name
        self.client = client
        self.running = False
        self._task: Optional[asyncio.Task] = None

    async def collect_cycle(self):
        """单次采集周期"""
        # 并发读取多个指标
        v_task = self.client.read_float(AppConfig.REG_VOLTAGE)
        c_task = self.client.read_float(AppConfig.REG_CURRENT)
        p_task = self.client.read_float(AppConfig.REG_POWER)
        
        results = await asyncio.gather(v_task, c_task, p_task, return_exceptions=True)
        
        # 解析结果
        voltage = results[0] if not isinstance(results[0], Exception) else None
        current = results[1] if not isinstance(results[1], Exception) else None
        power = results[2] if not isinstance(results[2], Exception) else None
        
        log_msg = f"📊 [{self.name}] "
        if voltage is not None: log_msg += f"电压: {voltage:.2f}V | "
        if current is not None: log_msg += f"电流: {current:.2f}A | "
        if power is not None:   log_msg += f"功率: {power:.2f}W"
        
        if voltage is None and current is None and power is None:
            logger.warning(f"⚠️ [{self.name}] 采集失败: 无法获取数据")
        else:
            logger.info(log_msg)

    async def start(self):
        """启动持续采集"""
        self.running = True
        logger.info(f"🚀 [{self.name}] 开始采集任务 (间隔 {AppConfig.COLLECT_INTERVAL}s)")
        
        while self.running:
            try:
                start_time = asyncio.get_running_loop().time()
                await self.collect_cycle()
                elapsed = asyncio.get_running_loop().time() - start_time
                
                # 计算剩余等待时间，保持固定周期
                wait_time = max(0.1, AppConfig.COLLECT_INTERVAL - elapsed)
                await asyncio.sleep(wait_time)
                
            except asyncio.CancelledError:
                logger.info(f"🛑 [{self.name}] 采集任务已取消")
                break
            except Exception as e:
                logger.error(f"❌ [{self.name}] 循环异常: {e}")
                await asyncio.sleep(1.0) # 出错后稍作等待

    def stop(self):
        """停止采集"""
        self.running = False
        logger.info(f"🛑 正在停止 [{self.name}]...")

# ==================== 模拟服务器 ====================
class ModbusSimulator:
    """Modbus TCP 模拟服务器"""
    
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.running = False
        self.context = None
        self.hr_block = None
        self._update_task = None

    def _init_store(self):
        """初始化寄存器存储区"""
        # 0-99 的保持寄存器
        self.hr_block = ModbusSequentialDataBlock(0, [0] * 100)
        
        # 初始值
        self.hr_block.setValues(AppConfig.REG_VOLTAGE, DataConverter.float_to_registers(220.0))
        self.hr_block.setValues(AppConfig.REG_CURRENT, DataConverter.float_to_registers(10.0))
        self.hr_block.setValues(AppConfig.REG_POWER,   DataConverter.float_to_registers(2200.0))
        
        store = ModbusDeviceContext(hr=self.hr_block)
        # 这里的 keys 是 slave_id
        self.context = ModbusServerContext(devices={AppConfig.SLAVE_ID: store}, single=False)

    async def _simulate_data_changes(self):
        """后台任务：模拟数据波动"""
        logger.info("🎲 数据模拟生成器已启动")
        voltage = 220.0
        current = 10.0
        
        while self.running:
            try:
                # 随机波动
                voltage += random.uniform(-1.0, 1.0)
                current += random.uniform(-0.5, 0.5)
                
                # 限制范围
                voltage = max(210.0, min(230.0, voltage))
                current = max(0.0, min(20.0, current))
                power = voltage * current
                
                # 更新寄存器
                self.hr_block.setValues(AppConfig.REG_VOLTAGE, DataConverter.float_to_registers(voltage))
                self.hr_block.setValues(AppConfig.REG_CURRENT, DataConverter.float_to_registers(current))
                self.hr_block.setValues(AppConfig.REG_POWER,   DataConverter.float_to_registers(power))
                
                await asyncio.sleep(0.5)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ 模拟数据更新出错: {e}")
                await asyncio.sleep(1)

    async def start(self):
        """启动服务器"""
        self._init_store()
        self.running = True
        
        # 启动数据模拟任务
        self._update_task = asyncio.create_task(self._simulate_data_changes())
        
        logger.info(f"🖥️ Modbus 服务器启动于 {self.host}:{self.port}")
        
        # StartAsyncTcpServer 启动服务器
        # 在 pymodbus 3.x 中，StartAsyncTcpServer 通常直接运行直到取消
        try:
            await StartAsyncTcpServer(
                context=self.context,
                address=(self.host, self.port),
            )
        except asyncio.CancelledError:
            logger.info("🛑 服务器任务被取消")
            raise

    async def stop(self):
        """停止服务器"""
        self.running = False
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
        logger.info("🛑 模拟服务器停止")

# ==================== 主流程 ====================
async def main():
    """主程序入口"""
    logger.info("="*40)
    logger.info("🚀 Modbus 模拟与采集系统启动")
    logger.info(f"配置: Host={AppConfig.HOST}, Port={AppConfig.PORT}, Slave={AppConfig.SLAVE_ID}")
    logger.info("操作: 按 Ctrl+C 停止运行")
    logger.info("="*40)

    # 1. 启动模拟服务器 (作为后台任务)
    simulator = ModbusSimulator(AppConfig.HOST, AppConfig.PORT)
    # StartAsyncTcpServer 会阻塞，所以我们必须用 create_task 把它放到后台
    server_task = asyncio.create_task(simulator.start())
    
    # 给服务器一点时间启动
    await asyncio.sleep(1.0)
    
    # 2. 启动采集客户端
    client_wrapper = ModbusClientWrapper(AppConfig.HOST, AppConfig.PORT, AppConfig.SLAVE_ID)
    collector = DeviceCollector("本地模拟设备", client_wrapper)
    
    # 采集任务
    collector_task = asyncio.create_task(collector.start())
    
    # 3. 运行直到被中断
    try:
        # 使用 Event 来等待，这样比 while True sleep 更优雅
        stop_event = asyncio.Event()
        await stop_event.wait()
    except asyncio.CancelledError:
        logger.info("⚠️ 主任务被取消")
    except KeyboardInterrupt:
        # 通常由 asyncio.run 捕获，但如果在此处捕获可以处理得更早
        logger.info("⚠️ 收到停止指令 (Ctrl+C)")
    finally:
        # 4. 优雅关闭资源
        logger.info("🔻 开始关闭系统资源...")
        
        # 停止采集
        collector.stop()
        collector_task.cancel()
        try:
            await collector_task
        except asyncio.CancelledError:
            pass
            
        # 断开客户端
        await client_wrapper.disconnect()
        
        # 停止服务器
        await simulator.stop()
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass
            
        logger.info("✅ 系统已完全停止")

if __name__ == "__main__":
    try:
        # 运行异步主程序
        asyncio.run(main())
    except KeyboardInterrupt:
        # 捕获最外层的 Ctrl+C，避免打印 traceback
        pass
