import time
from typing import Dict, List, Optional, Callable, Any

# ==========================================
# 1. 基础模型 (Data Model Base Classes)
# ==========================================

class DataAttribute:
    """
    DA (Data Attribute): 树叶。实际的数据值。
    例如: mag.f (幅值.浮点数)
    """
    def __init__(self, name: str, value: Any, parent=None):
        self.name = name
        self._value = value
        self.timestamp = time.time()
        self.quality = "good"
        self.parent = parent
        self.trigger_callbacks: List[Callable] = []

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_val):
        """
        核心机制: 当数据改变时，触发回调 (模拟 Report 机制)
        """
        if self._value != new_val:
            print(f"[IED Internal] Hardware Update: {self.get_full_path()} Changed {self._value} -> {new_val}")
            self._value = new_val
            self.timestamp = time.time()
            # 触发所有监听该数据的报告控制块
            for callback in self.trigger_callbacks:
                callback(self)

    def get_full_path(self) -> str:
        if self.parent:
            return f"{self.parent.get_full_path()}.{self.name}"
        return self.name

class DataObject:
    """
    DO (Data Object): 逻辑节点下的对象。
    例如: PhV (相电压), Pos (开关位置)
    """
    def __init__(self, name: str, parent=None):
        self.name = name
        self.parent = parent
        self.attributes: Dict[str, DataAttribute] = {}

    def add_da(self, name: str, value: Any) -> DataAttribute:
        da = DataAttribute(name, value, parent=self)
        self.attributes[name] = da
        return da

    def get_full_path(self) -> str:
        return f"{self.parent.get_full_path()}.{self.name}"

class LogicalNode:
    """
    LN (Logical Node): 最小功能单元。
    例如: MMXU (测量), XCBR (断路器)
    """
    def __init__(self, name: str, parent=None):
        self.name = name
        self.parent = parent
        self.objects: Dict[str, DataObject] = {}
        self.datasets: Dict[str, List[DataAttribute]] = {}
        self.reports: Dict[str, 'ReportControlBlock'] = {}

    def add_do(self, name: str) -> DataObject:
        do = DataObject(name, parent=self)
        self.objects[name] = do
        return do
    
    def create_dataset(self, name: str, da_list: List[DataAttribute]):
        """创建数据集 (购物车)"""
        self.datasets[name] = da_list
        print(f"[IED Config] Created DataSet: {name} with {len(da_list)} items")

    def create_report(self, name: str, dataset_name: str, rpt_id: str):
        """创建报告控制块 (快递单)"""
        if dataset_name not in self.datasets:
            raise ValueError(f"DataSet {dataset_name} not found")
        
        rcb = ReportControlBlock(name, rpt_id, self.datasets[dataset_name], parent=self)
        self.reports[name] = rcb
        return rcb

    def get_full_path(self) -> str:
        return f"{self.parent.get_full_path()}/{self.name}"

class LogicalDevice:
    """
    LD (Logical Device): 虚拟装置，功能分区。
    例如: Protection, Measurement
    """
    def __init__(self, name: str, parent=None):
        self.name = name
        self.parent = parent
        self.nodes: Dict[str, LogicalNode] = {}

    def add_ln(self, name: str) -> LogicalNode:
        ln = LogicalNode(name, parent=self)
        self.nodes[name] = ln
        return ln
    
    def get_full_path(self) -> str:
        return f"{self.name}" # LD作为根路径的一部分

class IecServer:
    """
    SERVER: 物理设备本身。
    """
    def __init__(self, name: str):
        self.name = name
        self.devices: Dict[str, LogicalDevice] = {}

    def add_ld(self, name: str) -> LogicalDevice:
        ld = LogicalDevice(name, parent=self)
        self.devices[name] = ld
        return ld

    def get_attribute_by_path(self, path: str) -> Optional[DataAttribute]:
        """
        通过字符串路径查找属性
        Format: LD/LN.DO.DA (Simplification)
        Real MMS path is complex, this is conceptual.
        """
        try:
            # Simple parser: Device/Node.Object.Attribute
            ld_name, rest = path.split('/', 1)
            ln_name, rest = rest.split('.', 1)
            do_name, da_name = rest.split('.', 1)
            
            return self.devices[ld_name].nodes[ln_name].objects[do_name].attributes[da_name]
        except Exception as e:
            print(f"Path lookup failed for {path}: {e}")
            return None

# ==========================================
# 2. 报告机制 (Reporting Mechanism)
# ==========================================

class ReportControlBlock:
    """
    RCB: 报告控制块。负责监听数据变化并发送报告。
    """
    def __init__(self, name: str, rpt_id: str, dataset: List[DataAttribute], parent: LogicalNode):
        self.name = name
        self.rpt_id = rpt_id
        self.dataset = dataset
        self.parent = parent
        self.enabled = False
        self.client_callback = None
        
        # 内部绑定: 告诉数据集里的每个DA，如果变了，通知我
        for da in self.dataset:
            da.trigger_callbacks.append(self.on_data_change)

    def enable(self, callback: Callable):
        self.client_callback = callback
        self.enabled = True
        print(f"[RCB] Report {self.name} ENABLED. Listening for changes...")

    def on_data_change(self, changed_da: DataAttribute):
        """
        当底层数据变化时被调用
        """
        if self.enabled and self.client_callback:
            print(f"[RCB] Triggered by {changed_da.name}. Sending Report...")
            # 构建报告内容 (包含当前数据集所有值)
            report_data = {da.get_full_path(): da.value for da in self.dataset}
            # 这里的 Reason 应该是 dchg (DataChange)
            self.client_callback(self.rpt_id, report_data, reason="dchg")
