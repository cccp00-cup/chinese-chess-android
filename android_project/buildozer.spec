[app]
# 应用标题
title = 中国象棋联机版

# 包名
package.name = chinese_chess_online

# 域名格式的包标识符
package.domain = org.chinesechess

# 应用版本
version = 1.0.0

# 要求的最低Android API级别
android.api = 31

# 目标Android API级别
android.ndk_api = 21

# 应用要求的权限
android.permissions = INTERNET, ACCESS_NETWORK_STATE, CHANGE_WIFI_STATE

# 应用图标
android.icon = chinese_new_year_icon_178470.ico

# 源代码目录
source.dir = .

# 主程序文件
source.main = android_main.py

# 包含的文件
source.include_exts = py,png,jpg,jpeg,js,css,html,txt,ico,json

# 包含的文件模式
source.include_patterns = chess.js,style.css,index.html,game_preview.html,interaction_guide.html,远程联机使用说明.txt

# 排除的文件
source.exclude_exts = spec,md
source.exclude_dirs = build,dist,__pycache__,.git

# 应用要求的Python版本
python.version = 3

# 要求的Python模块
requirements = python3,kivy==2.2.1,websockets>=11.0.0,pygame>=2.5.0,asyncio

# Android特定的元数据
android.meta_data = com.android.supports.PictureInPicture=true

# Android应用标签
android.app_label = 中国象棋联机版

# Android应用方向（landscape横屏，portrait竖屏）
android.orientation = landscape

# Android应用是否全屏
android.fullscreen = 0

# Android应用支持的架构
android.archs = arm64-v8a, armeabi-v7a

# 编译模式（debug或release）
android.build_mode = debug

[buildozer]

# Buildozer版本
buildozer.version = 1.5.0

# 使用的NDK版本
android.ndk = 23b

# 使用的SDK版本
android.sdk = 31

# 构建日志级别
log_level = 2

# 构建目录
build_dir = ./buildozer_build

# 缓存目录
cache_dir = ./buildozer_cache

# 输出目录
bin_dir = ./bin