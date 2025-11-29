#!/usr/bin/env python3
"""
中国象棋 - Kivy Launcher入口点
"""

import os
import sys

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入并运行主程序
from android_main import ChineseChessApp

if __name__ == "__main__":
    ChineseChessApp().run()
