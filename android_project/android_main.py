#!/usr/bin/env python3
"""
中国象棋 - Android版本主程序
基于Kivy框架开发
"""

import os
import sys
import asyncio

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from kivy.app import App
    from kivy.uix.widget import Widget
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.button import Button
    from kivy.uix.label import Label
    from kivy.uix.textinput import TextInput
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.floatlayout import FloatLayout
    from kivy.uix.popup import Popup
    from kivy.uix.screenmanager import ScreenManager, Screen
    from kivy.uix.slider import Slider
    from kivy.uix.switch import Switch
    from kivy.graphics import Color, Rectangle, Line, Ellipse
    from kivy.core.window import Window
    from kivy.clock import Clock
    from kivy.properties import StringProperty, ListProperty
except ImportError:
    print("Kivy未安装，请先安装: pip install kivy")
    sys.exit(1)

# 导入象棋逻辑
from chinese_chess import ChineseChess
from network_client import GameNetworkClient

class ChessBoardWidget(Widget):
    """象棋棋盘组件"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chess_game = ChineseChess()
        self.board_size = 9  # 9x10的棋盘
        self.cell_size = 40
        self.board_width = self.cell_size * 8
        self.board_height = self.cell_size * 9
        self.selected_piece = None
        self.valid_moves = []
        self.is_player_red = True
        self.network_client = None
        # 新增属性
        self.is_ai_game = False  # 是否AI对战
        self.ai_color = 'black'  # AI颜色
        self.is_two_player = False  # 是否双人对战
        
        # 设置组件大小
        self.size = (self.board_width + 100, self.board_height + 100)
        
        # 绘制棋盘
        self.draw_board()
        self.draw_pieces()
        
        # 移除了显式绑定，因为Widget已经有内置的on_touch_down方法
    
    def draw_board(self):
        """绘制棋盘"""
        with self.canvas:
            # 背景
            Color(0.9, 0.8, 0.6, 1)  # 木色背景
            Rectangle(pos=self.pos, size=self.size)
            
            # 棋盘线条
            Color(0, 0, 0, 1)
            Line(width=2)
            
            # 绘制横线
            for i in range(10):
                y = self.y + 50 + i * self.cell_size
                Line(points=[self.x + 50, y, self.x + 50 + self.board_width, y])
            
            # 绘制竖线
            for i in range(9):
                x = self.x + 50 + i * self.cell_size
                if i == 0 or i == 8:
                    # 两边完整竖线
                    Line(points=[x, self.y + 50, x, self.y + 50 + self.board_height])
                else:
                    # 中间分段竖线
                    Line(points=[x, self.y + 50, x, self.y + 50 + 4 * self.cell_size])
                    Line(points=[x, self.y + 50 + 5 * self.cell_size, x, self.y + 50 + 9 * self.cell_size])
            
            # 九宫格斜线
            # 红方九宫
            Line(points=[self.x + 50 + 3 * self.cell_size, self.y + 50, 
                        self.x + 50 + 5 * self.cell_size, self.y + 50 + 2 * self.cell_size])
            Line(points=[self.x + 50 + 5 * self.cell_size, self.y + 50,
                        self.x + 50 + 3 * self.cell_size, self.y + 50 + 2 * self.cell_size])
            
            # 黑方九宫
            Line(points=[self.x + 50 + 3 * self.cell_size, self.y + 50 + 7 * self.cell_size,
                        self.x + 50 + 5 * self.cell_size, self.y + 50 + 9 * self.cell_size])
            Line(points=[self.x + 50 + 5 * self.cell_size, self.y + 50 + 7 * self.cell_size,
                        self.x + 50 + 3 * self.cell_size, self.y + 50 + 9 * self.cell_size])
    
    def draw_pieces(self):
        """绘制棋子"""
        # 清除画布
        self.canvas.clear()
        # 清除所有子组件（Label）
        self.clear_widgets()
        # 重新绘制棋盘
        self.draw_board()
        
        # 绘制所有棋子
        board = self.chess_game.board
        for row in range(10):
            for col in range(9):
                piece = board[row][col]
                if piece:
                    self.draw_piece(piece, col, row)
    
    def draw_piece(self, piece, col, row):
        """绘制单个棋子"""
        x = self.x + 50 + col * self.cell_size
        y = self.y + 50 + row * self.cell_size
        
        # 绘制棋子背景和边框
        with self.canvas:
            # 棋子背景圆
            if piece.color == 'red':
                Color(1, 0.2, 0.2, 1)  # 红色
            else:
                Color(0.1, 0.1, 0.1, 1)  # 黑色
            
            # 增大棋子大小以适应更大的字体
            Ellipse(pos=(x - 18, y - 18), size=(36, 36))
            
            # 棋子边框
            Color(0, 0, 0, 1)
            Line(circle=(x, y, 18), width=2)
        
        # 创建一个简单的Label来显示棋子文字
        piece_char = piece.get_display_char()
        # 优化文字显示：增大字体，加粗，确保居中显示
        label = Label(
            text=piece_char, 
            font_size=28, 
            bold=True, 
            halign='center', 
            valign='middle',
            text_size=(36, 36),  # 设置文本大小，确保文本居中
            size=(36, 36),  # 设置Label大小与棋子大小匹配
            pos=(x - 18, y - 18),  # 设置Label位置与棋子位置匹配
            font_name='simhei'  # 使用黑体字体，支持中文显示
        )
        self.add_widget(label)
    
    def on_touch_down(self, touch):
        """处理棋盘触摸事件"""
        # 确保组件已经添加到窗口
        if not self.parent:
            return False
        
        # 计算点击的格子，使用组件的局部坐标
        local_pos = self.to_local(touch.x, touch.y)
        col = int((local_pos[0] - 50) / self.cell_size)
        row = int((local_pos[1] - 50) / self.cell_size)
        
        if 0 <= col < 9 and 0 <= row < 10:
            self.handle_cell_click(col, row)
            return True
        return super(ChessBoardWidget, self).on_touch_down(touch)
    
    def handle_cell_click(self, col, row):
        """处理格子点击"""
        board = self.chess_game.board
        piece = board[row][col]
        
        # 清除之前的所有子组件（避免Label重复添加）
        self.clear_widgets()
        
        if self.selected_piece:
            # 尝试移动
            from_row, from_col = self.selected_piece
            if self.chess_game.move_piece(from_row, from_col, row, col):
                self.selected_piece = None
                self.valid_moves = []
                self.draw_pieces()
                
                # 更新游戏状态
                game_status = self.chess_game.get_game_status()
                if game_status != 'playing':
                    self.show_game_result(game_status)
                
                # 网络对战时发送移动
                if self.network_client:
                    self.send_move_to_network(from_row, from_col, row, col)
                
                # AI对战模式下，AI自动移动
                if self.is_ai_game and self.chess_game.get_current_player() == self.ai_color:
                    # 延迟执行AI移动，让玩家有时间看到移动结果
                    Clock.schedule_once(lambda dt: self.ai_move(), 0.5)
            else:
                # 移动无效，取消选择
                self.selected_piece = None
                self.valid_moves = []
                self.draw_pieces()
        else:
            # 选择棋子
            if piece:
                # 检查是否是当前玩家的回合
                if piece.color == self.chess_game.get_current_player():
                    # 检查是否是玩家的棋子，双人对战模式下可以操控双方
                    if self.is_two_player or (piece.color == 'red' and self.is_player_red) or (piece.color == 'black' and not self.is_player_red):
                        self.selected_piece = (row, col)
                        # 获取有效移动，注意参数顺序是(row, col)
                        self.valid_moves = self.chess_game.get_valid_moves(row, col)
                        self.draw_pieces()
                        self.highlight_selected()
                        self.highlight_valid_moves()
                    else:
                        self.draw_pieces()
                else:
                    self.draw_pieces()
            else:
                self.draw_pieces()
    
    def highlight_valid_moves(self):
        """高亮显示有效移动"""
        with self.canvas:
            Color(0, 1, 0, 0.5)  # 绿色半透明
            for move in self.valid_moves:
                row, col = move
                x = self.x + 50 + col * self.cell_size
                y = self.y + 50 + row * self.cell_size
                Ellipse(pos=(x - 8, y - 8), size=(16, 16))
    
    def highlight_selected(self):
        """高亮选中的棋子"""
        if self.selected_piece:
            row, col = self.selected_piece
            x = self.x + 50 + col * self.cell_size
            y = self.y + 50 + row * self.cell_size
            
            with self.canvas:
                Color(1, 1, 0, 1)  # 黄色高亮
                Line(circle=(x, y, 20), width=3)
    
    def send_move_to_network(self, from_row, from_col, to_row, to_col):
        """发送移动信息到网络"""
        if self.network_client:
            # 使用异步方式发送移动
            import asyncio
            asyncio.run(self.network_client.send_move(from_row, from_col, to_row, to_col))
    
    def on_network_connected(self):
        """网络连接成功"""
        print("网络连接成功")
    
    def on_network_error(self, error_code, error_message):
        """网络错误"""
        print(f"网络错误: {error_code} - {error_message}")
    
    def on_room_list_received(self, rooms):
        """收到房间列表"""
        print(f"收到房间列表: {rooms}")
    
    def on_room_updated(self, room_info):
        """房间更新"""
        print(f"房间更新: {room_info}")
    
    def on_network_game_start(self, players, current_player):
        """网络对战开始"""
        print(f"网络对战开始: 玩家 {players}, 当前玩家 {current_player}")
    
    def on_network_game_move(self, from_row, from_col, to_row, to_col):
        """收到对手移动"""
        if self.chess_game.move_piece(from_row, from_col, to_row, to_col):
            self.draw_pieces()
            # 更新游戏状态
            game_status = self.chess_game.get_game_status()
            if game_status != 'playing':
                self.show_game_result(game_status)
    
    def on_network_game_state(self, current_player, game_status):
        """游戏状态更新"""
        print(f"游戏状态更新: 当前玩家 {current_player}, 状态 {game_status}")
    
    def on_network_game_restart(self):
        """游戏重新开始"""
        print("游戏重新开始")
        self.chess_game.reset()
        self.draw_pieces()
    
    def ai_move(self):
        """AI移动"""
        import random
        
        # 获取所有有效的AI移动
        all_valid_moves = []
        board = self.chess_game.board
        
        # 遍历所有棋子，找到AI的棋子
        for row in range(10):
            for col in range(9):
                piece = board[row][col]
                if piece and piece.color == self.ai_color:
                    # 获取该棋子的所有有效移动
                    valid_moves = self.chess_game.get_valid_moves(row, col)
                    for move in valid_moves:
                        all_valid_moves.append((row, col, move[0], move[1]))
        
        if all_valid_moves:
            # 随机选择一个有效的移动
            from_row, from_col, to_row, to_col = random.choice(all_valid_moves)
            
            # 执行移动
            if self.chess_game.move_piece(from_row, from_col, to_row, to_col):
                # 清除选择和有效移动
                self.selected_piece = None
                self.valid_moves = []
                self.draw_pieces()
                
                # 更新游戏状态
                game_status = self.chess_game.get_game_status()
                if game_status != 'playing':
                    self.show_game_result(game_status)
    
    def show_game_result(self, result):
        """显示游戏结果"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        if result == 'red_wins':
            content.add_widget(Label(text='红方获胜！', font_size=24, bold=True))
        else:
            content.add_widget(Label(text='黑方获胜！', font_size=24, bold=True))
        
        close_btn = Button(text='返回主菜单', size_hint_y=None, height=40, bold=True)
        content.add_widget(close_btn)
        
        popup = Popup(title='游戏结束', content=content, size_hint=(0.7, 0.5))
        
        def on_close(instance):
            popup.dismiss()
            # 找到ScreenManager并返回主菜单
            parent = self.parent
            while parent and not isinstance(parent, ScreenManager):
                parent = parent.parent
            if parent:
                parent.current = 'main_menu'
        
        close_btn.bind(on_press=on_close)
        popup.open()


class MainMenuScreen(Screen):
    """主菜单界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'main_menu'
        self.build_ui()
    
    def build_ui(self):
        """构建UI"""
        # 使用FloatLayout作为主布局，方便添加背景和装饰元素
        main_layout = FloatLayout()
        
        # 添加背景色
        with main_layout.canvas.before:
            Color(0.1, 0.2, 0.3, 1)  # 深蓝色背景
            Rectangle(pos=(0, 0), size=(Window.width, Window.height))
        
        # 创建垂直布局用于放置主要内容
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20, size_hint=(0.8, 0.8), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        
        # 标题
        title = Label(
            text='中国象棋',
            font_size=56,
            size_hint_y=0.3,
            color=(1, 0.3, 0.3, 1),
            bold=True,
            italic=True,
            font_name='simhei'  # 使用黑体字体，支持中文显示
        )
        layout.add_widget(title)
        
        # 按钮容器
        button_layout = BoxLayout(orientation='vertical', spacing=15, size_hint_y=0.6, padding=10)
        
        # 单机对战按钮
        single_player_btn = Button(
            text='单机对战',
            height=70,
            background_color=(0.2, 0.7, 0.2, 1),
            font_size=24,
            bold=True,
            border=(10, 10, 10, 10),
            color=(1, 1, 1, 1),
            font_name='simhei'  # 使用黑体字体，支持中文显示
        )
        single_player_btn.bind(on_press=self.start_single_player)
        button_layout.add_widget(single_player_btn)
        
        # 联机对战按钮
        online_btn = Button(
            text='联机对战',
            size_hint_y=None,
            height=70,
            background_color=(0.2, 0.5, 0.9, 1),
            font_size=24,
            bold=True,
            border=(10, 10, 10, 10),
            color=(1, 1, 1, 1),
            font_name='simhei'  # 使用黑体字体，支持中文显示
        )
        online_btn.bind(on_press=self.start_online_game)
        button_layout.add_widget(online_btn)
        
        # 网络对战按钮
        network_btn = Button(
            text='网络对战',
            size_hint_y=None,
            height=70,
            background_color=(0.9, 0.5, 0.2, 1),
            font_size=24,
            bold=True,
            border=(10, 10, 10, 10),
            color=(1, 1, 1, 1),
            font_name='simhei'  # 使用黑体字体，支持中文显示
        )
        network_btn.bind(on_press=self.start_network_game)
        button_layout.add_widget(network_btn)
        
        # 设置按钮
        settings_btn = Button(
            text='设置',
            size_hint_y=None,
            height=70,
            background_color=(0.7, 0.7, 0.7, 1),
            font_size=24,
            bold=True,
            border=(10, 10, 10, 10),
            color=(0, 0, 0, 1),
            font_name='simhei'  # 使用黑体字体，支持中文显示
        )
        settings_btn.bind(on_press=self.open_settings)
        button_layout.add_widget(settings_btn)
        
        layout.add_widget(button_layout)
        main_layout.add_widget(layout)
        self.add_widget(main_layout)
    
    def start_single_player(self, instance):
        """开始单机对战"""
        # 创建选择玩家颜色的对话框
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        content.add_widget(Label(text='选择玩家颜色', font_size=20, bold=True, font_name='simhei'))
        
        # 按钮容器
        btn_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)
        
        red_btn = Button(text='红方', font_size=18, bold=True, font_name='simhei')
        red_btn.bind(on_press=lambda x: self.start_game_with_color('red'))
        btn_layout.add_widget(red_btn)
        
        black_btn = Button(text='黑方', font_size=18, bold=True, font_name='simhei')
        black_btn.bind(on_press=lambda x: self.start_game_with_color('black'))
        btn_layout.add_widget(black_btn)
        
        two_player_btn = Button(text='双人对战', font_size=18, bold=True, font_name='simhei')
        two_player_btn.bind(on_press=lambda x: self.start_two_player_game())
        btn_layout.add_widget(two_player_btn)
        
        content.add_widget(btn_layout)
        
        self.color_select_popup = Popup(
            title='选择玩家颜色',
            content=content,
            size_hint=(0.8, 0.4)
        )
        self.color_select_popup.open()
    
    def start_game_with_color(self, color):
        """根据选择的颜色开始游戏"""
        self.manager.current = 'game'
        game_screen = self.manager.get_screen('game')
        if game_screen.chess_board:
            game_screen.chess_board.is_player_red = (color == 'red')
            # 设置AI对战模式
            game_screen.chess_board.is_ai_game = True
            game_screen.chess_board.ai_color = 'black' if color == 'red' else 'red'
        self.color_select_popup.dismiss()
    
    def start_two_player_game(self):
        """开始双人对战"""
        self.manager.current = 'game'
        game_screen = self.manager.get_screen('game')
        if game_screen.chess_board:
            # 双人对战模式，玩家可以操控双方
            game_screen.chess_board.is_player_red = True
            game_screen.chess_board.is_two_player = True
        self.color_select_popup.dismiss()
    
    def start_online_game(self, instance):
        """开始联机对战"""
        self.manager.current = 'game'
        # 这里可以添加联机逻辑
    
    def start_network_game(self, instance):
        """开始网络对战"""
        self.show_network_dialog()
    
    def open_settings(self, instance):
        """打开设置"""
        self.show_settings_dialog()
    
    def show_settings_dialog(self):
        """显示设置对话框"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 标题
        content.add_widget(Label(text='游戏设置', font_size=20, bold=True, font_name='simhei'))
        
        # 音量设置
        volume_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        volume_layout.add_widget(Label(text='音量:', font_size=16, font_name='simhei'))
        volume_slider = Slider(min=0, max=100, value=70, size_hint_x=0.8)
        volume_layout.add_widget(volume_slider)
        volume_label = Label(text='70', size_hint_x=0.2, font_size=16, font_name='simhei')
        volume_layout.add_widget(volume_label)
        content.add_widget(volume_layout)
        
        # 音效开关
        sound_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        sound_layout.add_widget(Label(text='音效:', font_size=16, font_name='simhei'))
        sound_switch = Switch(active=True, size_hint_x=0.8)
        sound_layout.add_widget(sound_switch)
        content.add_widget(sound_layout)
        
        # 震动开关
        vibration_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        vibration_layout.add_widget(Label(text='震动:', font_size=16, font_name='simhei'))
        vibration_switch = Switch(active=True, size_hint_x=0.8)
        vibration_layout.add_widget(vibration_switch)
        content.add_widget(vibration_layout)
        
        # 按钮容器
        btn_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)
        
        save_btn = Button(text='保存设置', font_size=18, bold=True, font_name='simhei')
        save_btn.bind(on_press=lambda x: self.save_settings(self.settings_popup))
        btn_layout.add_widget(save_btn)
        
        cancel_btn = Button(text='取消', font_size=18, bold=True, font_name='simhei')
        cancel_btn.bind(on_press=lambda x: self.settings_popup.dismiss())
        btn_layout.add_widget(cancel_btn)
        
        content.add_widget(btn_layout)
        
        self.settings_popup = Popup(title='设置', content=content, size_hint=(0.8, 0.6))
        self.settings_popup.open()
    
    def save_settings(self, popup):
        """保存设置"""
        # 这里可以添加保存设置的逻辑
        popup.dismiss()
        # 显示保存成功提示
        success_popup = Popup(
            title='成功',
            content=Label(text='设置已保存', font_size=18, font_name='simhei'),
            size_hint=(0.5, 0.3)
        )
        success_popup.open()
    
    def show_network_dialog(self):
        """显示网络连接对话框"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 玩家名称输入
        content.add_widget(Label(text='玩家名称:', font_size=16, bold=True, font_name='simhei'))
        player_input = TextInput(
            text='玩家1',
            multiline=False,
            size_hint_y=None,
            height=40,
            font_size=16,
            font_name='simhei'  # 使用黑体字体，支持中文显示
        )
        content.add_widget(player_input)
        
        # 服务器地址输入
        content.add_widget(Label(text='服务器地址:', font_size=16, bold=True, font_name='simhei'))
        server_input = TextInput(
            text='ws://localhost:8766',
            multiline=False,
            size_hint_y=None,
            height=40,
            font_size=16,
            font_name='simhei'  # 使用黑体字体，支持中文显示
        )
        content.add_widget(server_input)
        
        # 按钮容器
        btn_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)
        
        connect_btn = Button(text='连接', font_size=18, bold=True, font_name='simhei')
        connect_btn.bind(on_press=lambda x: self.connect_to_server(server_input.text, player_input.text))
        btn_layout.add_widget(connect_btn)
        
        cancel_btn = Button(text='取消', font_size=18, bold=True, font_name='simhei')
        cancel_btn.bind(on_press=lambda x: self.network_popup.dismiss())
        btn_layout.add_widget(cancel_btn)
        
        content.add_widget(btn_layout)
        
        self.network_popup = Popup(
            title='网络对战设置',
            content=content,
            size_hint=(0.8, 0.4)
        )
        self.network_popup.open()
    
    def connect_to_server(self, server_url, player_name):
        """连接到服务器"""
        try:
            game_screen = self.manager.get_screen('game')
            # 初始化GameNetworkClient，传递game_instance
            game_screen.chess_board.network_client = GameNetworkClient(game_screen.chess_board)
            game_screen.chess_board.is_player_red = False  # 网络对战默认黑方
            self.manager.current = 'game'
            self.network_popup.dismiss()
        except Exception as e:
            self.show_error(f"连接失败: {str(e)}")
    
    def show_error(self, message):
        """显示错误信息"""
        popup = Popup(
            title='错误',
            content=Label(text=message, font_size=16, bold=True),
            size_hint=(0.6, 0.3)
        )
        popup.open()


class GameScreen(Screen):
    """游戏界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'game'
        self.chess_board = None
        self.move_history = []  # 用于悔棋的移动历史
        self.build_ui()
        
        # 定时更新游戏状态
        Clock.schedule_interval(self.update_game_status, 0.5)
    
    def build_ui(self):
        """构建UI"""
        layout = BoxLayout(orientation='vertical')
        
        # 顶部信息栏
        info_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=10)
        
        self.status_label = Label(
            text='红方回合',
            size_hint_x=0.6,
            font_size=24,
            bold=True,
            font_name='simhei'  # 使用黑体字体，支持中文显示
        )
        info_layout.add_widget(self.status_label)
        
        # 返回按钮
        back_btn = Button(
            text='返回主菜单',
            size_hint_x=0.4,
            font_size=16,
            bold=True,
            font_name='simhei'  # 使用黑体字体，支持中文显示
        )
        back_btn.bind(on_press=self.back_to_menu)
        info_layout.add_widget(back_btn)
        
        layout.add_widget(info_layout)
        
        # 棋盘区域
        self.chess_board = ChessBoardWidget()
        scroll_view = ScrollView(size_hint_y=0.8, do_scroll_x=False, do_scroll_y=False)
        scroll_view.add_widget(self.chess_board)
        layout.add_widget(scroll_view)
        
        # 底部控制栏
        control_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=10)
        
        restart_btn = Button(text='重新开始', font_size=18, bold=True, font_name='simhei')
        restart_btn.bind(on_press=self.restart_game)
        control_layout.add_widget(restart_btn)
        
        undo_btn = Button(text='悔棋', font_size=18, bold=True, font_name='simhei')
        undo_btn.bind(on_press=self.undo_move)
        control_layout.add_widget(undo_btn)
        
        layout.add_widget(control_layout)
        
        self.add_widget(layout)
    
    def back_to_menu(self, instance):
        """返回主菜单"""
        self.manager.current = 'main_menu'
    
    def restart_game(self, instance):
        """重新开始游戏"""
        if self.chess_board:
            self.chess_board.chess_game = ChineseChess()
            self.chess_board.selected_piece = None
            self.chess_board.valid_moves = []
            self.chess_board.draw_pieces()
            self.move_history = []
            self.status_label.text = '红方回合'
    
    def undo_move(self, instance):
        """悔棋"""
        if self.chess_board:
            if self.chess_board.chess_game.undo_move():
                self.chess_board.selected_piece = None
                self.chess_board.valid_moves = []
                self.chess_board.draw_pieces()
                # 更新游戏状态显示
                game = self.chess_board.chess_game
                current_player = game.get_current_player()
                self.status_label.text = f'{"红方" if current_player == "red" else "黑方"}回合'
    
    def update_game_status(self, dt):
        """更新游戏状态显示"""
        if self.chess_board:
            game = self.chess_board.chess_game
            current_player = game.get_current_player()
            game_status = game.get_game_status()
            
            if game_status == 'playing':
                self.status_label.text = f'{"红方" if current_player == "red" else "黑方"}回合'
            else:
                self.status_label.text = f'{"红方获胜" if game_status == "red_wins" else "黑方获胜"}'


class ChineseChessApp(App):
    """中国象棋Kivy应用"""
    
    def build(self):
        """构建应用"""
        self.title = '中国象棋'
        self.icon = 'chinese_new_year_icon_178470.ico'
        
        # 创建屏幕管理器
        sm = ScreenManager()
        
        # 添加屏幕
        sm.add_widget(MainMenuScreen())
        sm.add_widget(GameScreen())
        
        return sm
    
    def on_pause(self):
        """应用暂停时调用（Android）"""
        return True
    
    def on_resume(self):
        """应用恢复时调用（Android）"""
        pass


if __name__ == '__main__':
    # Android设备上的特殊处理
    if hasattr(sys, 'getandroidapilevel'):
        # 在Android上运行时的特殊配置
        Window.fullscreen = False
        Window.show_cursor = True
    
    ChineseChessApp().run()