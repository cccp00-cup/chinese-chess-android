from enum import Enum

class PieceType(Enum):
    GENERAL = "将帅"
    ADVISOR = "士仕"
    ELEPHANT = "象相"
    HORSE = "马馬"
    CHARIOT = "车車"
    CANNON = "炮砲"
    SOLDIER = "兵卒"

class Piece:
    def __init__(self, piece_type, color, row, col):
        self.type = piece_type
        self.color = color
        self.row = row
        self.col = col
        self.is_selected = False
    
    def get_display_char(self):
        """获取棋子的显示字符"""
        piece_chars = {
            PieceType.GENERAL: '帅',
            PieceType.ADVISOR: '仕',
            PieceType.ELEPHANT: '相',
            PieceType.HORSE: '马',
            PieceType.CHARIOT: '车',
            PieceType.CANNON: '炮',
            PieceType.SOLDIER: '兵'
        }
        
        black_piece_chars = {
            PieceType.GENERAL: '将',
            PieceType.ADVISOR: '士',
            PieceType.ELEPHANT: '象',
            PieceType.HORSE: '馬',
            PieceType.CHARIOT: '車',
            PieceType.CANNON: '砲',
            PieceType.SOLDIER: '卒'
        }
        
        if self.color == 'red':
            return piece_chars[self.type]
        else:
            return black_piece_chars[self.type]

class ChineseChess:
    def __init__(self):
        # 游戏状态
        self.board = [[None for _ in range(9)] for _ in range(10)]
        self.current_player = 'red'
        self.selected_piece = None
        self.game_status = 'playing'
        self.valid_moves = []
        self.move_history = []  # 用于悔棋的移动历史
        
        self.initialize_board()
    
    def initialize_board(self):
        """初始化棋盘"""
        # 黑方棋子 (上方)
        black_setup = [
            ['車', '馬', '象', '士', '将', '士', '象', '馬', '車'],
            [None, None, None, None, None, None, None, None, None],
            [None, '砲', None, None, None, None, None, '砲', None],
            ['卒', None, '卒', None, '卒', None, '卒', None, '卒'],
            [None, None, None, None, None, None, None, None, None]
        ]
        
        # 红方棋子 (下方)
        red_setup = [
            [None, None, None, None, None, None, None, None, None],
            ['兵', None, '兵', None, '兵', None, '兵', None, '兵'],
            [None, '炮', None, None, None, None, None, '炮', None],
            [None, None, None, None, None, None, None, None, None],
            ['車', '馬', '相', '仕', '帅', '仕', '相', '馬', '車']
        ]
        
        # 放置黑方棋子
        for row in range(5):
            for col in range(9):
                if black_setup[row][col]:
                    piece_map = {
                        '車': PieceType.CHARIOT, '馬': PieceType.HORSE, '象': PieceType.ELEPHANT,
                        '士': PieceType.ADVISOR, '将': PieceType.GENERAL, '砲': PieceType.CANNON,
                        '卒': PieceType.SOLDIER
                    }
                    self.board[row][col] = Piece(piece_map[black_setup[row][col]], 'black', row, col)
        
        # 放置红方棋子
        for row in range(5, 10):
            for col in range(9):
                if red_setup[row - 5][col]:
                    piece_map = {
                        '車': PieceType.CHARIOT, '馬': PieceType.HORSE, '相': PieceType.ELEPHANT,
                        '仕': PieceType.ADVISOR, '帅': PieceType.GENERAL, '炮': PieceType.CANNON,
                        '兵': PieceType.SOLDIER
                    }
                    self.board[row][col] = Piece(piece_map[red_setup[row - 5][col]], 'red', row, col)
    
    def is_in_palace(self, color, row, col):
        """检查是否在宫殿内"""
        if color == 'red':
            return 7 <= row <= 9 and 3 <= col <= 5
        else:
            return 0 <= row <= 2 and 3 <= col <= 5
    
    def get_general_moves(self, row, col, color):
        """将帅的移动"""
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if self.is_in_palace(color, new_row, new_col):
                if not self.board[new_row][new_col] or self.board[new_row][new_col].color != color:
                    moves.append((new_row, new_col))
        
        return moves
    
    def get_advisor_moves(self, row, col, color):
        """士的移动"""
        moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if self.is_in_palace(color, new_row, new_col):
                if not self.board[new_row][new_col] or self.board[new_row][new_col].color != color:
                    moves.append((new_row, new_col))
        
        return moves
    
    def get_elephant_moves(self, row, col, color):
        """象的移动"""
        moves = []
        directions = [(-2, -2), (-2, 2), (2, -2), (2, 2)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            
            # 检查是否过河
            if (color == 'red' and new_row < 5) or (color == 'black' and new_row > 4):
                continue
            
            # 检查象眼是否被阻挡
            block_row, block_col = row + dr // 2, col + dc // 2
            if 0 <= block_row < 10 and 0 <= block_col < 9 and not self.board[block_row][block_col]:
                if 0 <= new_row < 10 and 0 <= new_col < 9:
                    if not self.board[new_row][new_col] or self.board[new_row][new_col].color != color:
                        moves.append((new_row, new_col))
        
        return moves
    
    def get_horse_moves(self, row, col, color):
        """马的移动"""
        moves = []
        directions = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                     (1, -2), (1, 2), (2, -1), (2, 1)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            
            # 检查马腿是否被阻挡
            block_row, block_col = 0, 0
            if abs(dr) == 2:
                block_row, block_col = row + dr // 2, col
            else:
                block_row, block_col = row, col + dc // 2
            
            if 0 <= block_row < 10 and 0 <= block_col < 9 and not self.board[block_row][block_col]:
                if 0 <= new_row < 10 and 0 <= new_col < 9:
                    if not self.board[new_row][new_col] or self.board[new_row][new_col].color != color:
                        moves.append((new_row, new_col))
        
        return moves
    
    def get_chariot_moves(self, row, col, color):
        """车的移动"""
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            while 0 <= new_row < 10 and 0 <= new_col < 9:
                target_piece = self.board[new_row][new_col]
                if target_piece:
                    if target_piece.color != color:
                        moves.append((new_row, new_col))
                    break
                moves.append((new_row, new_col))
                new_row += dr
                new_col += dc
        
        return moves
    
    def get_cannon_moves(self, row, col, color):
        """炮的移动"""
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            has_barrier = False
            
            while 0 <= new_row < 10 and 0 <= new_col < 9:
                target_piece = self.board[new_row][new_col]
                
                if target_piece:
                    if not has_barrier:
                        has_barrier = True
                    else:
                        if target_piece.color != color:
                            moves.append((new_row, new_col))
                        break
                elif not has_barrier:
                    moves.append((new_row, new_col))
                
                new_row += dr
                new_col += dc
        
        return moves
    
    def get_soldier_moves(self, row, col, color):
        """兵卒的移动"""
        moves = []
        
        if color == 'red':
            # 红方兵
            if row > 0:
                if not self.board[row - 1][col] or self.board[row - 1][col].color != color:
                    moves.append((row - 1, col))
            
            # 过河后可以左右移动
            if row <= 4:  # 已过河
                if col > 0 and (not self.board[row][col - 1] or self.board[row][col - 1].color != color):
                    moves.append((row, col - 1))
                if col < 8 and (not self.board[row][col + 1] or self.board[row][col + 1].color != color):
                    moves.append((row, col + 1))
        else:
            # 黑方卒
            if row < 9:
                if not self.board[row + 1][col] or self.board[row + 1][col].color != color:
                    moves.append((row + 1, col))
            
            # 过河后可以左右移动
            if row >= 5:  # 已过河
                if col > 0 and (not self.board[row][col - 1] or self.board[row][col - 1].color != color):
                    moves.append((row, col - 1))
                if col < 8 and (not self.board[row][col + 1] or self.board[row][col + 1].color != color):
                    moves.append((row, col + 1))
        
        return moves
    
    def get_valid_moves(self, row, col):
        """获取棋子的合法移动"""
        piece = self.board[row][col]
        if not piece:
            return []
        
        moves = []
        piece_type = piece.type
        
        # 根据棋子类型获取移动
        if piece_type == PieceType.GENERAL:  # 将帅
            moves = self.get_general_moves(row, col, piece.color)
        elif piece_type == PieceType.ADVISOR:  # 士
            moves = self.get_advisor_moves(row, col, piece.color)
        elif piece_type == PieceType.ELEPHANT:  # 象
            moves = self.get_elephant_moves(row, col, piece.color)
        elif piece_type == PieceType.HORSE:  # 马
            moves = self.get_horse_moves(row, col, piece.color)
        elif piece_type == PieceType.CHARIOT:  # 车
            moves = self.get_chariot_moves(row, col, piece.color)
        elif piece_type == PieceType.CANNON:  # 炮
            moves = self.get_cannon_moves(row, col, piece.color)
        elif piece_type == PieceType.SOLDIER:  # 兵卒
            moves = self.get_soldier_moves(row, col, piece.color)
        
        return moves
    
    def move_piece(self, from_row, from_col, to_row, to_col):
        """移动棋子"""
        piece = self.board[from_row][from_col]
        if not piece:
            return False
        
        # 检查是否是当前玩家的棋子
        if piece.color != self.current_player:
            return False
        
        # 检查移动是否合法
        valid_moves = self.get_valid_moves(from_row, from_col)
        if (to_row, to_col) not in valid_moves:
            return False
        
        # 保存移动前的状态用于悔棋
        captured_piece = self.board[to_row][to_col]
        move_info = {
            'from_row': from_row,
            'from_col': from_col,
            'to_row': to_row,
            'to_col': to_col,
            'moved_piece': piece,
            'captured_piece': captured_piece,
            'current_player': self.current_player
        }
        self.move_history.append(move_info)
        
        # 执行移动
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        piece.row = to_row
        piece.col = to_col
        
        # 切换玩家
        self.current_player = 'black' if self.current_player == 'red' else 'red'
        
        # 检查游戏状态
        self.check_game_status()
        
        return True
    
    def undo_move(self):
        """悔棋"""
        if not self.move_history:
            return False
        
        # 获取最后一步移动
        move_info = self.move_history.pop()
        
        # 恢复移动前的状态
        from_row = move_info['from_row']
        from_col = move_info['from_col']
        to_row = move_info['to_row']
        to_col = move_info['to_col']
        moved_piece = move_info['moved_piece']
        captured_piece = move_info['captured_piece']
        
        # 恢复棋子位置
        self.board[from_row][from_col] = moved_piece
        self.board[to_row][to_col] = captured_piece
        moved_piece.row = from_row
        moved_piece.col = from_col
        
        # 恢复当前玩家
        self.current_player = move_info['current_player']
        
        # 恢复游戏状态为进行中
        self.game_status = 'playing'
        
        return True
    
    def check_game_status(self):
        """检查游戏状态"""
        # 简化版本：检查是否有将帅被吃掉
        red_general = False
        black_general = False
        
        for row in range(10):
            for col in range(9):
                piece = self.board[row][col]
                if piece and piece.type == PieceType.GENERAL:
                    if piece.color == 'red':
                        red_general = True
                    else:
                        black_general = True
        
        if not red_general:
            self.game_status = 'black_wins'
        elif not black_general:
            self.game_status = 'red_wins'
        else:
            self.game_status = 'playing'
    
    def get_game_status(self):
        """获取游戏状态"""
        return self.game_status
    
    def get_current_player(self):
        """获取当前玩家"""
        return self.current_player
