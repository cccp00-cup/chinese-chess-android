#!/usr/bin/env python3
"""
PyDroid运行脚本
"""

import os
import sys

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 运行主程序
if __name__ == "__main__":
    from android_main import ChineseChessApp
    ChineseChessApp().run()
