#!/usr/bin/env python3
"""
PyDroid安装脚本
"""

import subprocess
import sys

def install_requirements():
    """安装依赖"""
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✓ 依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 安装失败: {e}")
        return False

if __name__ == "__main__":
    print("开始安装依赖...")
    if install_requirements():
        print("可以运行 android_main.py 开始游戏了！")
    else:
        print("请手动安装 requirements.txt 中的依赖")
