from typing import Dict, Any, Callable
try:
    from .model import IecServer
except ImportError:
    from model import IecServer

class IecClient:
    """
    Client (MMS Client): 模拟主站系统/你的代码。
    """
    def __init__(self):
        self.connected_server: IecServer = None
        self.report_handlers: Dict[str, Callable] = {}

    def connect(self, server: IecServer, ip: str = "192.168.1.100"):
        """
        模拟 TCP 连接过程 (关联上 Server 对象)
        """
        print(f"[Client] Connecting to {ip}...")
        self.connected_server = server
        print(f"[Client] Connected to Server: {server.name}")

    def get_server_directory(self):
        """
        MMS GetNameList: 获取模型结构
        """
        print("\n[Client] Discovery (Browsing Model)...")
        if not self.connected_server:
            print("Error: Not connected")
            return

        for ld_name, ld in self.connected_server.devices.items():
            print(f"  +- LD: {ld_name}")
            for ln_name, ln in ld.nodes.items():
                print(f"     +- LN: {ln_name}")
                for do_name, do in ln.objects.items():
                    print(f"        +- DO: {do_name}")
                    for da_name, da in do.attributes.items():
                        print(f"           - DA: {da_name} = {da.value}")
        print("[Client] Discovery Complete.\n")

    def read_value(self, path: str):
        """
        MMS Read: 主动读取
        """
        if not self.connected_server:
            return None
        
        print(f"[ClientRequest] READ {path}")
        da = self.connected_server.get_attribute_by_path(path)
        if da:
            print(f"[ClientResponse] Value: {da.value} (Time: {da.timestamp})")
            return da.value
        else:
            print(f"[ClientResponse] Error: Path not found")
            return None

    def enable_report(self, ld_name: str, ln_name: str, rcb_name: str):
        """
        MMS Write: 激活报告控制块 (Enable RCB)
        """
        print(f"[ClientRequest] Enable Report: {rcb_name}")
        try:
            # 找到 RCB 对象 (模拟 MMS 寻址)
            ld = self.connected_server.devices[ld_name]
            ln = ld.nodes[ln_name]
            rcb = ln.reports[rcb_name]
            
            # 注册回调函数 (OnReport)
            rcb.enable(self._on_report_received)
            print(f"[ClientResponse] Success. Report Enabled.")
        except KeyError:
            print(f"[ClientResponse] Error: RCB not found")

    def _on_report_received(self, rpt_id: str, data: Dict[str, Any], reason: str):
        """
        回调函数: 当收到 Server 推送的报告时执行
        """
        print(f"\n⚡⚡ [Client Event] REPORT RECEIVED ⚡⚡")
        print(f"  Report ID: {rpt_id}")
        print(f"  Reason: {reason}")
        print(f"  Data Content:")
        for path, val in data.items():
            print(f"    {path} : {val}")
        print(f"⚡⚡ [End Report] ⚡⚡\n")
