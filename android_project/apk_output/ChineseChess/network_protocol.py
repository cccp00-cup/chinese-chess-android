"""
网络通信协议定义
用于中国象棋联机版本的网络通信
"""

from enum import Enum
import json

class MessageType(Enum):
    """消息类型枚举"""
    # 连接相关
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    
    # 房间相关
    CREATE_ROOM = "create_room"
    JOIN_ROOM = "join_room"
    LEAVE_ROOM = "leave_room"
    ROOM_LIST = "room_list"
    ROOM_UPDATE = "room_update"
    
    # 游戏相关
    GAME_START = "game_start"
    GAME_MOVE = "game_move"
    GAME_STATE = "game_state"
    GAME_END = "game_end"
    GAME_RESTART = "game_restart"
    
    # 玩家相关
    PLAYER_READY = "player_ready"
    PLAYER_LIST = "player_list"
    
    # 错误信息
    ERROR = "error"
    SUCCESS = "success"

class NetworkMessage:
    """网络消息基类"""
    
    def __init__(self, message_type, data=None, player_id=None):
        self.type = message_type
        self.data = data or {}
        self.player_id = player_id
        self.timestamp = None
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'type': self.type.value,
            'data': self.data,
            'player_id': self.player_id,
            'timestamp': self.timestamp
        }
    
    def to_json(self):
        """转换为JSON字符串"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str):
        """从JSON字符串创建消息"""
        try:
            data = json.loads(json_str)
            msg = cls(MessageType(data['type']), data.get('data'), data.get('player_id'))
            msg.timestamp = data.get('timestamp')
            return msg
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise ValueError(f"Invalid message format: {e}")

# 具体消息类型定义
class ConnectMessage(NetworkMessage):
    """连接消息"""
    def __init__(self, player_name, player_id=None):
        super().__init__(MessageType.CONNECT, {
            'player_name': player_name
        }, player_id)

class CreateRoomMessage(NetworkMessage):
    """创建房间消息"""
    def __init__(self, room_name, max_players=2, player_id=None):
        super().__init__(MessageType.CREATE_ROOM, {
            'room_name': room_name,
            'max_players': max_players
        }, player_id)

class JoinRoomMessage(NetworkMessage):
    """加入房间消息"""
    def __init__(self, room_id, player_id=None):
        super().__init__(MessageType.JOIN_ROOM, {
            'room_id': room_id
        }, player_id)

class GameMoveMessage(NetworkMessage):
    """游戏移动消息"""
    def __init__(self, from_row, from_col, to_row, to_col, player_id=None):
        super().__init__(MessageType.GAME_MOVE, {
            'from_row': from_row,
            'from_col': from_col,
            'to_row': to_row,
            'to_col': to_col
        }, player_id)

class GameStateMessage(NetworkMessage):
    """游戏状态消息"""
    def __init__(self, board_state, current_player, game_status, player_id=None):
        super().__init__(MessageType.GAME_STATE, {
            'board_state': board_state,
            'current_player': current_player,
            'game_status': game_status
        }, player_id)

class PlayerReadyMessage(NetworkMessage):
    """玩家准备消息"""
    def __init__(self, is_ready, player_id=None):
        super().__init__(MessageType.PLAYER_READY, {
            'is_ready': is_ready
        }, player_id)

class ErrorMessage(NetworkMessage):
    """错误消息"""
    def __init__(self, error_code, error_message, player_id=None):
        super().__init__(MessageType.ERROR, {
            'error_code': error_code,
            'error_message': error_message
        }, player_id)

# 错误码定义
class ErrorCode:
    """错误码定义"""
    SUCCESS = 0
    ROOM_FULL = 1001
    ROOM_NOT_FOUND = 1002
    INVALID_MOVE = 1003
    NOT_YOUR_TURN = 1004
    GAME_NOT_STARTED = 1005
    PLAYER_NOT_IN_ROOM = 1006
    NETWORK_ERROR = 2001
    SERVER_ERROR = 2002

# 游戏状态定义
class GameStatus:
    """游戏状态定义"""
    WAITING = "waiting"
    PLAYING = "playing"
    RED_WINS = "red_wins"
    BLACK_WINS = "black_wins"
    DRAW = "draw"

# 玩家状态定义
class PlayerStatus:
    """玩家状态定义"""
    ONLINE = "online"
    IN_ROOM = "in_room"
    READY = "ready"
    PLAYING = "playing"
    OFFLINE = "offline"