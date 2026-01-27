"""
快速启动脚本 - Modbus 模拟器测试
直接运行模拟器示例，无需修改代码
"""
# -*- coding: utf-8 -*-

import asyncio
import sys
import os
import io

# 设置输出编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sim_modbus import main as example_with_simulator


async def main():
    """主函数"""
    print("\n" + "="*60)
    print("Modbus 模拟器快速启动")
    print("="*60)
    print("\n提示：")
    print("- 服务器地址: 127.0.0.1:5020")
    print("- 采集时间: 10 秒")
    print("- 采集间隔: 1 秒")
    print("- 按 Ctrl+C 可随时停止")
    print("\n" + "="*60 + "\n")
    
    try:
        await example_with_simulator()
    except KeyboardInterrupt:
        print("\n\n[中断] 用户中断")
    except Exception as e:
        print(f"\n\n[错误] 程序异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

