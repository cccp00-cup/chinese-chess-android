"""
中国象棋客户端网络管理器
"""

import asyncio
import websockets
import json
import threading
from datetime import datetime
from network_protocol import *
from network_config import network_config
from nat_traversal import nat_traversal_manager, domain_resolver

class NetworkManager:
    """网络连接管理器"""
    
    def __init__(self, server_url=None):
        # 使用网络配置
        client_config = network_config.get_client_config()
        self.server_url = server_url or client_config['server_url']
        self.max_reconnect_attempts = client_config['reconnect_attempts']
        self.reconnect_delay = client_config['reconnect_delay']
        self.connection_timeout = client_config['connection_timeout']
        
        self.websocket = None
        self.is_connected = False
        self.player_id = None
        self.player_name = None
        self.message_handlers = {}
        self.running = False
        self.receive_thread = None
        self.reconnect_attempts = 0
        self.nat_info = None
        self.peer_connections = {}  # peer_id -> websocket
        
    def register_message_handler(self, message_type, handler):
        """注册消息处理器"""
        self.message_handlers[message_type] = handler
    
    def unregister_message_handler(self, message_type):
        """注销消息处理器"""
        if message_type in self.message_handlers:
            del self.message_handlers[message_type]
    
    async def connect(self, server_url, player_name):
        """连接到服务器"""
        try:
            self.websocket = await websockets.connect(server_url)
            self.player_name = player_name
            self.is_connected = True
            self.reconnect_attempts = 0
            
            # 发送连接消息
            connect_msg = ConnectMessage(player_name)
            await self.send_message(connect_msg)
            
            # 启动接收消息线程
            self.running = True
            self.receive_thread = threading.Thread(target=self._receive_messages)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            
            print(f"已连接到服务器: {server_url}")
            return True
            
        except Exception as e:
            print(f"连接服务器失败: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """断开连接"""
        self.running = False
        self.is_connected = False
        
        if self.websocket:
            try:
                await self.websocket.close()
            except:
                pass
            self.websocket = None
        
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join(timeout=1)
        
        print("已断开与服务器的连接")
    
    async def send_message(self, message):
        """发送消息到服务器"""
        if not self.is_connected or not self.websocket:
            print("未连接到服务器")
            return False
        
        try:
            json_message = message.to_json()
            await self.websocket.send(json_message)
            print(f"发送消息: {message.type.value}")
            return True
        except Exception as e:
            print(f"发送消息失败: {e}")
            self.is_connected = False
            return False
    
    def _receive_messages(self):
        """接收消息的线程函数"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._receive_loop())
    
    async def _receive_loop(self):
        """接收消息循环"""
        while self.running and self.is_connected and self.websocket:
            try:
                message = await self.websocket.recv()
                await self._handle_received_message(message)
            except websockets.exceptions.ConnectionClosed:
                print("与服务器的连接已关闭")
                self.is_connected = False
                break
            except Exception as e:
                print(f"接收消息时出错: {e}")
                self.is_connected = False
                break
        
        # 尝试重连
        if self.running and self.reconnect_attempts < self.max_reconnect_attempts:
            await self._attempt_reconnect()
    
    async def _handle_received_message(self, message):
        """处理接收到的消息"""
        try:
            network_message = NetworkMessage.from_json(message)
            print(f"收到消息: {network_message.type.value}")
            
            # 处理连接响应
            if network_message.type == MessageType.CONNECT:
                self.player_id = network_message.data.get('player_id')
                print(f"分配的玩家ID: {self.player_id}")
            
            # 调用注册的消息处理器
            if network_message.type in self.message_handlers:
                handler = self.message_handlers[network_message.type]
                await handler(network_message)
            else:
                print(f"未找到消息处理器: {network_message.type.value}")
                
        except Exception as e:
            print(f"处理消息时出错: {e}")
    
    async def _attempt_reconnect(self):
        """尝试重连"""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            print("重连失败，已达到最大重连次数")
            return
        
        self.reconnect_attempts += 1
        print(f"尝试第{self.reconnect_attempts}次重连到 {self.server_url}...")
        
        await asyncio.sleep(self.reconnect_delay)
        
        # 使用当前配置的服务器地址重新连接
        success = await self.connect(self.server_url, self.player_name)
        
        if success:
            print("重连成功！")
        else:
            print("重连失败")
    
    # 快捷消息发送方法
    async def create_room(self, room_name, max_players=2):
        """创建房间"""
        message = CreateRoomMessage(room_name, max_players, self.player_id)
        return await self.send_message(message)
    
    async def join_room(self, room_id):
        """加入房间"""
        message = JoinRoomMessage(room_id, self.player_id)
        return await self.send_message(message)
    
    async def leave_room(self):
        """离开房间"""
        message = NetworkMessage(MessageType.LEAVE_ROOM, {}, self.player_id)
        return await self.send_message(message)
    
    async def send_game_move(self, from_row, from_col, to_row, to_col):
        """发送游戏移动"""
        message = GameMoveMessage(from_row, from_col, to_row, to_col, self.player_id)
        return await self.send_message(message)
    
    async def set_player_ready(self, is_ready):
        """设置玩家准备状态"""
        message = PlayerReadyMessage(is_ready, self.player_id)
        return await self.send_message(message)
    
    async def request_room_list(self):
        """请求房间列表"""
        message = NetworkMessage(MessageType.ROOM_LIST, {}, self.player_id)
        return await self.send_message(message)
    
    async def restart_game(self):
        """请求重新开始游戏"""
        message = NetworkMessage(MessageType.GAME_RESTART, {}, self.player_id)
        return await self.send_message(message)
    
    async def discover_nat_info(self):
        """发现NAT信息"""
        if network_config.is_nat_traverse_enabled():
            self.nat_info = await nat_traversal_manager.discover_nat_info()
            if self.nat_info:
                print(f"NAT信息发现成功: {self.nat_info.public_ip}:{self.nat_info.public_port}")
                # 将NAT信息发送到服务器
                await self.send_nat_info()
            return self.nat_info
        return None
    
    async def send_nat_info(self):
        """发送NAT信息到服务器"""
        if self.is_connected and self.nat_info:
            nat_info_message = {
                "type": "nat_info",
                "public_ip": self.nat_info.public_ip,
                "public_port": self.nat_info.public_port,
                "local_ip": self.nat_info.local_ip,
                "local_port": self.nat_info.local_port,
                "nat_type": self.nat_info.nat_type,
                "is_behind_nat": self.nat_info.is_behind_nat
            }
            await self.send_message(nat_info_message)
    
    async def establish_p2p_connection(self, target_peer_id: str):
        """建立P2P连接"""
        if not network_config.is_nat_traverse_enabled():
            print("NAT穿透功能已禁用")
            return None
        
        # 发现NAT信息（如果尚未发现）
        if not self.nat_info:
            await self.discover_nat_info()
        
        # 尝试建立P2P连接
        p2p_url = await nat_traversal_manager.establish_p2p_connection(target_peer_id)
        if p2p_url:
            try:
                # 解析域名
                parsed_url = p2p_url.replace("ws://", "").split(":")
                host = parsed_url[0]
                port = int(parsed_url[1]) if len(parsed_url) > 1 else 8766
                
                # 解析域名
                resolved_host = await domain_resolver.resolve_domain(host)
                resolved_url = f"ws://{resolved_host}:{port}"
                
                # 建立WebSocket连接
                websocket = await websockets.connect(resolved_url)
                self.peer_connections[target_peer_id] = websocket
                
                print(f"P2P连接建立成功: {target_peer_id} -> {resolved_url}")
                return websocket
                
            except Exception as e:
                print(f"P2P连接建立失败: {target_peer_id}, 错误: {e}")
        
        return None
    
    async def close_p2p_connection(self, target_peer_id: str):
        """关闭P2P连接"""
        if target_peer_id in self.peer_connections:
            websocket = self.peer_connections[target_peer_id]
            await websocket.close()
            del self.peer_connections[target_peer_id]
            print(f"P2P连接已关闭: {target_peer_id}")
    
    async def send_p2p_message(self, target_peer_id: str, message: dict):
        """发送P2P消息"""
        if target_peer_id in self.peer_connections:
            websocket = self.peer_connections[target_peer_id]
            try:
                message_json = json.dumps(message)
                await websocket.send(message_json)
            except Exception as e:
                print(f"P2P消息发送失败: {target_peer_id}, 错误: {e}")
                # 如果发送失败，尝试重新建立连接
                await self.close_p2p_connection(target_peer_id)
                await self.establish_p2p_connection(target_peer_id)
    
    async def handle_p2p_message(self, websocket, message: dict):
        """处理P2P消息"""
        message_type = message.get("type")
        
        if message_type == "p2p_game_move":
            # 处理P2P游戏移动
            await self.handle_p2p_game_move(message)
        elif message_type == "p2p_game_sync":
            # 处理P2P游戏同步
            await self.handle_p2p_game_sync(message)
        elif message_type == "p2p_chat_message":
            # 处理P2P聊天消息
            await self.handle_p2p_chat_message(message)
    
    async def handle_p2p_game_move(self, message: dict):
        """处理P2P游戏移动"""
        # 这里可以调用游戏逻辑处理函数
        print(f"收到P2P游戏移动: {message}")
        # 触发游戏移动事件
        if "p2p_game_move" in self.message_handlers:
            await self.message_handlers["p2p_game_move"](message)
    
    async def handle_p2p_game_sync(self, message: dict):
        """处理P2P游戏同步"""
        print(f"收到P2P游戏同步: {message}")
        if "p2p_game_sync" in self.message_handlers:
            await self.message_handlers["p2p_game_sync"](message)
    
    async def handle_p2p_chat_message(self, message: dict):
        """处理P2P聊天消息"""
        print(f"收到P2P聊天消息: {message}")
        if "p2p_chat_message" in self.message_handlers:
            await self.message_handlers["p2p_chat_message"](message)

class GameNetworkClient:
    """游戏网络客户端，集成到现有游戏中"""
    
    def __init__(self, game_instance):
        self.network_manager = NetworkManager()
        self.game = game_instance
        self.current_room = None
        self.is_host = False
        
        # 注册消息处理器
        self._register_handlers()
    
    def _register_handlers(self):
        """注册网络消息处理器"""
        self.network_manager.register_message_handler(MessageType.CONNECT, self._on_connect)
        self.network_manager.register_message_handler(MessageType.SUCCESS, self._on_success)
        self.network_manager.register_message_handler(MessageType.ERROR, self._on_error)
        self.network_manager.register_message_handler(MessageType.ROOM_LIST, self._on_room_list)
        self.network_manager.register_message_handler(MessageType.ROOM_UPDATE, self._on_room_update)
        self.network_manager.register_message_handler(MessageType.GAME_START, self._on_game_start)
        self.network_manager.register_message_handler(MessageType.GAME_MOVE, self._on_game_move)
        self.network_manager.register_message_handler(MessageType.GAME_STATE, self._on_game_state)
        self.network_manager.register_message_handler(MessageType.GAME_RESTART, self._on_game_restart)
    
    async def connect_to_server(self, server_url, player_name):
        """连接到游戏服务器"""
        return await self.network_manager.connect(server_url, player_name)
    
    async def disconnect_from_server(self):
        """断开与服务器的连接"""
        await self.network_manager.disconnect()
    
    # 消息处理器
    async def _on_connect(self, message):
        """处理连接成功"""
        print("连接服务器成功")
        if hasattr(self.game, 'on_network_connected'):
            self.game.on_network_connected()
    
    async def _on_success(self, message):
        """处理成功消息"""
        print(f"操作成功: {message.data.get('message', '')}")
        
        # 如果是创建房间成功，设置为主机
        if 'room_id' in message.data:
            self.current_room = message.data['room_id']
            self.is_host = True
    
    async def _on_error(self, message):
        """处理错误消息"""
        error_code = message.data.get('error_code', 0)
        error_message = message.data.get('error_message', '未知错误')
        print(f"错误 [{error_code}]: {error_message}")
        
        if hasattr(self.game, 'on_network_error'):
            self.game.on_network_error(error_code, error_message)
    
    async def _on_room_list(self, message):
        """处理房间列表"""
        rooms = message.data.get('rooms', [])
        print(f"收到房间列表: {len(rooms)} 个房间")
        
        if hasattr(self.game, 'on_room_list_received'):
            self.game.on_room_list_received(rooms)
    
    async def _on_room_update(self, message):
        """处理房间更新"""
        room_info = message.data.get('room_info', {})
        print(f"房间更新: {room_info.get('room_name', '')}")
        
        if hasattr(self.game, 'on_room_updated'):
            self.game.on_room_updated(room_info)
    
    async def _on_game_start(self, message):
        """处理游戏开始"""
        print("游戏开始！")
        players = message.data.get('players', [])
        current_player = message.data.get('current_player', 'red')
        
        if hasattr(self.game, 'on_network_game_start'):
            self.game.on_network_game_start(players, current_player)
    
    async def _on_game_move(self, message):
        """处理游戏移动"""
        from_row = message.data.get('from_row')
        from_col = message.data.get('from_col')
        to_row = message.data.get('to_row')
        to_col = message.data.get('to_col')
        
        print(f"收到对手移动: ({from_row},{from_col}) -> ({to_row},{to_col})")
        
        if hasattr(self.game, 'on_network_game_move'):
            self.game.on_network_game_move(from_row, from_col, to_row, to_col)
    
    async def _on_game_state(self, message):
        """处理游戏状态更新"""
        current_player = message.data.get('current_player')
        game_status = message.data.get('game_status')
        
        print(f"游戏状态更新: 当前玩家 {current_player}, 状态 {game_status}")
        
        if hasattr(self.game, 'on_network_game_state'):
            self.game.on_network_game_state(current_player, game_status)
    
    async def _on_game_restart(self, message):
        """处理游戏重新开始"""
        print("收到游戏重新开始消息")
        if hasattr(self.game, 'on_network_game_restart'):
            self.game.on_network_game_restart()
    
    # 快捷方法
    async def create_room(self, room_name, max_players=2):
        """创建房间"""
        return await self.network_manager.create_room(room_name, max_players)
    
    async def join_room(self, room_id):
        """加入房间"""
        self.current_room = room_id
        self.is_host = False
        return await self.network_manager.join_room(room_id)
    
    async def leave_room(self):
        """离开房间"""
        self.current_room = None
        self.is_host = False
        return await self.network_manager.leave_room()
    
    async def send_move(self, from_row, from_col, to_row, to_col):
        """发送移动"""
        return await self.network_manager.send_game_move(from_row, from_col, to_row, to_col)
    
    async def set_ready(self, is_ready):
        """设置准备状态"""
        return await self.network_manager.set_player_ready(is_ready)
    
    async def get_room_list(self):
        """获取房间列表"""
        return await self.network_manager.request_room_list()
    
    async def request_restart_game(self):
        """请求重新开始游戏"""
        return await self.network_manager.restart_game()