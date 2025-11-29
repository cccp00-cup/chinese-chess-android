class ChineseChess {
    constructor() {
        this.board = [];
        this.currentPlayer = 'red';
        this.selectedPiece = null;
        this.gameStatus = 'playing';
        this.capturedPieces = {
            red: [],
            black: []
        };
        
        this.pieceTypes = {
            '帅': 'general', '将': 'general',
            '仕': 'advisor', '士': 'advisor',
            '相': 'elephant', '象': 'elephant',
            '馬': 'horse', '马': 'horse',
            '車': 'chariot', '车': 'chariot',
            '炮': 'cannon', '砲': 'cannon',
            '兵': 'soldier', '卒': 'soldier'
        };
        
        this.init();
    }
    
    init() {
        this.initializeBoard();
        this.renderBoard();
        this.bindEvents();
        this.updateGameInfo();
    }
    
    initializeBoard() {
        this.board = Array(10).fill(null).map(() => Array(9).fill(null));
        
        const initialSetup = [
            // 黑方 (上方)
            ['車', '馬', '象', '士', '将', '士', '象', '馬', '車'],
            [null, null, null, null, null, null, null, null, null],
            [null, '砲', null, null, null, null, null, '砲', null],
            ['卒', null, '卒', null, '卒', null, '卒', null, '卒'],
            [null, null, null, null, null, null, null, null, null],
            
            // 红方 (下方)
            [null, null, null, null, null, null, null, null, null],
            ['兵', null, '兵', null, '兵', null, '兵', null, '兵'],
            [null, '炮', null, null, null, null, null, '炮', null],
            [null, null, null, null, null, null, null, null, null],
            ['車', '馬', '相', '仕', '帅', '仕', '相', '馬', '車']
        ];
        
        for (let row = 0; row < 10; row++) {
            for (let col = 0; col < 9; col++) {
                if (initialSetup[row][col]) {
                    this.board[row][col] = {
                        type: initialSetup[row][col],
                        color: row < 5 ? 'black' : 'red',
                        row: row,
                        col: col
                    };
                }
            }
        }
    }
    
    renderBoard() {
        const boardElement = document.getElementById('chess-board');
        boardElement.innerHTML = '';
        
        // 创建棋盘网格
        const grid = document.createElement('div');
        grid.className = 'board-grid';
        
        for (let row = 0; row < 10; row++) {
            const rowElement = document.createElement('div');
            rowElement.className = 'board-row';
            
            for (let col = 0; col < 9; col++) {
                const cell = document.createElement('div');
                cell.className = 'board-cell';
                cell.dataset.row = row;
                cell.dataset.col = col;
                
                // 添加棋子
                if (this.board[row][col]) {
                    const piece = this.createPieceElement(this.board[row][col]);
                    cell.appendChild(piece);
                }
                
                rowElement.appendChild(cell);
            }
            grid.appendChild(rowElement);
        }
        
        boardElement.appendChild(grid);
        
        // 添加楚河汉界
        const river = document.createElement('div');
        river.className = 'river';
        river.textContent = '楚河汉界';
        boardElement.appendChild(river);
        
        // 添加宫殿
        const redPalace = document.createElement('div');
        redPalace.className = 'palace palace-red';
        boardElement.appendChild(redPalace);
        
        const blackPalace = document.createElement('div');
        blackPalace.className = 'palace palace-black';
        boardElement.appendChild(blackPalace);
    }
    
    createPieceElement(piece) {
        const pieceElement = document.createElement('div');
        pieceElement.className = `piece ${piece.color}`;
        pieceElement.textContent = piece.type;
        pieceElement.dataset.type = piece.type;
        pieceElement.dataset.color = piece.color;
        pieceElement.dataset.row = piece.row;
        pieceElement.dataset.col = piece.col;
        return pieceElement;
    }
    
    bindEvents() {
        document.getElementById('chess-board').addEventListener('click', (e) => {
            if (this.gameStatus !== 'playing') return;
            
            const cell = e.target.closest('.board-cell');
            const piece = e.target.closest('.piece');
            
            if (piece) {
                this.handlePieceClick(piece);
            } else if (cell) {
                this.handleCellClick(cell);
            }
        });
        
        document.getElementById('restart-btn').addEventListener('click', () => {
            this.restart();
        });
    }
    
    handlePieceClick(pieceElement) {
        const row = parseInt(pieceElement.dataset.row);
        const col = parseInt(pieceElement.dataset.col);
        const piece = this.board[row][col];
        
        if (!piece) return;
        
        if (piece.color === this.currentPlayer) {
            this.selectPiece(piece, row, col);
        } else if (this.selectedPiece) {
            this.attemptMove(row, col);
        }
    }
    
    handleCellClick(cellElement) {
        if (this.selectedPiece) {
            const row = parseInt(cellElement.dataset.row);
            const col = parseInt(cellElement.dataset.col);
            this.attemptMove(row, col);
        }
    }
    
    selectPiece(piece, row, col) {
        this.clearSelection();
        this.selectedPiece = { piece, row, col };
        
        // 高亮选中的棋子
        const pieceElement = document.querySelector(`[data-row="${row}"][data-col="${col}"] .piece`);
        if (pieceElement) {
            pieceElement.classList.add('selected');
        }
        
        // 显示合法移动
        this.showValidMoves(piece, row, col);
    }
    
    clearSelection() {
        document.querySelectorAll('.selected').forEach(el => el.classList.remove('selected'));
        document.querySelectorAll('.valid-move').forEach(el => el.classList.remove('valid-move'));
        document.querySelectorAll('.valid-capture').forEach(el => el.classList.remove('valid-capture'));
        this.selectedPiece = null;
    }
    
    showValidMoves(piece, row, col) {
        const validMoves = this.getValidMoves(piece, row, col);
        
        validMoves.forEach(move => {
            const cell = document.querySelector(`[data-row="${move.row}"][data-col="${move.col}"]`);
            if (cell) {
                if (move.capture) {
                    cell.classList.add('valid-capture');
                } else {
                    cell.classList.add('valid-move');
                }
            }
        });
    }
    
    getValidMoves(piece, row, col) {
        const moves = [];
        const pieceType = this.pieceTypes[piece.type];
        
        switch (pieceType) {
            case 'general':
                moves.push(...this.getGeneralMoves(piece, row, col));
                break;
            case 'advisor':
                moves.push(...this.getAdvisorMoves(piece, row, col));
                break;
            case 'elephant':
                moves.push(...this.getElephantMoves(piece, row, col));
                break;
            case 'horse':
                moves.push(...this.getHorseMoves(piece, row, col));
                break;
            case 'chariot':
                moves.push(...this.getChariotMoves(piece, row, col));
                break;
            case 'cannon':
                moves.push(...this.getCannonMoves(piece, row, col));
                break;
            case 'soldier':
                moves.push(...this.getSoldierMoves(piece, row, col));
                break;
        }
        
        return moves.filter(move => {
            if (move.row < 0 || move.row > 9 || move.col < 0 || move.col > 8) return false;
            
            const targetPiece = this.board[move.row][move.col];
            if (targetPiece && targetPiece.color === piece.color) return false;
            
            move.capture = targetPiece && targetPiece.color !== piece.color;
            return true;
        });
    }
    
    getGeneralMoves(piece, row, col) {
        const moves = [];
        const directions = [[-1, 0], [1, 0], [0, -1], [0, 1]];
        
        // 将军的移动限制在宫殿内
        const isInPalace = this.isInPalace(piece.color, row, col);
        
        directions.forEach(([dr, dc]) => {
            const newRow = row + dr;
            const newCol = col + dc;
            
            if (isInPalace && this.isInPalace(piece.color, newRow, newCol)) {
                moves.push({ row: newRow, col: newCol });
            }
        });
        
        return moves;
    }
    
    getAdvisorMoves(piece, row, col) {
        const moves = [];
        const directions = [[-1, -1], [-1, 1], [1, -1], [1, 1]];
        
        directions.forEach(([dr, dc]) => {
            const newRow = row + dr;
            const newCol = col + dc;
            
            if (this.isInPalace(piece.color, newRow, newCol)) {
                moves.push({ row: newRow, col: newCol });
            }
        });
        
        return moves;
    }
    
    getElephantMoves(piece, row, col) {
        const moves = [];
        const directions = [[-2, -2], [-2, 2], [2, -2], [2, 2]];
        
        directions.forEach(([dr, dc]) => {
            const newRow = row + dr;
            const newCol = col + dc;
            
            // 象不能过河
            if ((piece.color === 'red' && newRow < 5) || (piece.color === 'black' && newRow > 4)) {
                return;
            }
            
            // 检查象眼是否被阻挡
            const blockRow = row + dr / 2;
            const blockCol = col + dc / 2;
            
            if (!this.board[blockRow][blockCol]) {
                moves.push({ row: newRow, col: newCol });
            }
        });
        
        return moves;
    }
    
    getHorseMoves(piece, row, col) {
        const moves = [];
        const directions = [
            [-2, -1], [-2, 1], [-1, -2], [-1, 2],
            [1, -2], [1, 2], [2, -1], [2, 1]
        ];
        
        directions.forEach(([dr, dc]) => {
            const newRow = row + dr;
            const newCol = col + dc;
            
            // 检查马腿是否被阻挡
            let blockRow, blockCol;
            if (Math.abs(dr) === 2) {
                blockRow = row + dr / 2;
                blockCol = col;
            } else {
                blockRow = row;
                blockCol = col + dc / 2;
            }
            
            if (!this.board[blockRow][blockCol]) {
                moves.push({ row: newRow, col: newCol });
            }
        });
        
        return moves;
    }
    
    getChariotMoves(piece, row, col) {
        const moves = [];
        const directions = [[-1, 0], [1, 0], [0, -1], [0, 1]];
        
        directions.forEach(([dr, dc]) => {
            let newRow = row + dr;
            let newCol = col + dc;
            
            while (newRow >= 0 && newRow < 10 && newCol >= 0 && newCol < 9) {
                const targetPiece = this.board[newRow][newCol];
                
                if (targetPiece) {
                    if (targetPiece.color !== piece.color) {
                        moves.push({ row: newRow, col: newCol });
                    }
                    break;
                }
                
                moves.push({ row: newRow, col: newCol });
                newRow += dr;
                newCol += dc;
            }
        });
        
        return moves;
    }
    
    getCannonMoves(piece, row, col) {
        const moves = [];
        const directions = [[-1, 0], [1, 0], [0, -1], [0, 1]];
        
        directions.forEach(([dr, dc]) => {
            let newRow = row + dr;
            let newCol = col + dc;
            let hasBarrier = false;
            
            while (newRow >= 0 && newRow < 10 && newCol >= 0 && newCol < 9) {
                const targetPiece = this.board[newRow][newCol];
                
                if (targetPiece) {
                    if (!hasBarrier) {
                        hasBarrier = true;
                    } else {
                        if (targetPiece.color !== piece.color) {
                            moves.push({ row: newRow, col: newCol });
                        }
                        break;
                    }
                } else if (!hasBarrier) {
                    moves.push({ row: newRow, col: newCol });
                }
                
                newRow += dr;
                newCol += dc;
            }
        });
        
        return moves;
    }
    
    getSoldierMoves(piece, row, col) {
        const moves = [];
        const isCrossedRiver = this.hasCrossedRiver(piece.color, row);
        
        if (piece.color === 'red') {
            moves.push({ row: row - 1, col: col });
            if (isCrossedRiver) {
                moves.push({ row: row, col: col - 1 });
                moves.push({ row: row, col: col + 1 });
            }
        } else {
            moves.push({ row: row + 1, col: col });
            if (isCrossedRiver) {
                moves.push({ row: row, col: col - 1 });
                moves.push({ row: row, col: col + 1 });
            }
        }
        
        return moves;
    }
    
    isInPalace(color, row, col) {
        if (color === 'red') {
            return row >= 7 && row <= 9 && col >= 3 && col <= 5;
        } else {
            return row >= 0 && row <= 2 && col >= 3 && col <= 5;
        }
    }
    
    hasCrossedRiver(color, row) {
        if (color === 'red') {
            return row <= 4;
        } else {
            return row >= 5;
        }
    }
    
    attemptMove(targetRow, targetCol) {
        if (!this.selectedPiece) return;
        
        const { piece, row, col } = this.selectedPiece;
        const validMoves = this.getValidMoves(piece, row, col);
        
        const move = validMoves.find(m => m.row === targetRow && m.col === targetCol);
        if (!move) return;
        
        // 执行移动
        this.executeMove(piece, row, col, targetRow, targetCol, move.capture);
        
        // 切换玩家
        this.currentPlayer = this.currentPlayer === 'red' ? 'black' : 'red';
        this.clearSelection();
        this.updateGameInfo();
        this.renderBoard();
        
        // 检查游戏状态
        this.checkGameStatus();
    }
    
    executeMove(piece, fromRow, fromCol, toRow, toCol, capture) {
        if (capture) {
            const capturedPiece = this.board[toRow][toCol];
            this.capturedPieces[this.currentPlayer].push(capturedPiece);
            this.updateCapturedPieces();
        }
        
        this.board[toRow][toCol] = piece;
        this.board[fromRow][fromCol] = null;
        piece.row = toRow;
        piece.col = toCol;
    }
    
    updateCapturedPieces() {
        const redCaptured = document.getElementById('captured-red');
        const blackCaptured = document.getElementById('captured-black');
        
        redCaptured.innerHTML = this.capturedPieces['black'].map(piece => 
            `<div class="captured-piece red">${piece.type}</div>`
        ).join('');
        
        blackCaptured.innerHTML = this.capturedPieces['red'].map(piece => 
            `<div class="captured-piece black">${piece.type}</div>`
        ).join('');
    }
    
    checkGameStatus() {
        const redGeneral = this.findGeneral('red');
        const blackGeneral = this.findGeneral('black');
        
        if (!redGeneral) {
            this.gameStatus = 'black_wins';
        } else if (!blackGeneral) {
            this.gameStatus = 'red_wins';
        } else {
            // 检查是否被将死
            const isRedInCheck = this.isInCheck('red');
            const isBlackInCheck = this.isInCheck('black');
            
            if (isRedInCheck && this.isCheckmate('red')) {
                this.gameStatus = 'black_wins';
            } else if (isBlackInCheck && this.isCheckmate('black')) {
                this.gameStatus = 'red_wins';
            }
        }
        
        this.updateGameInfo();
    }
    
    findGeneral(color) {
        for (let row = 0; row < 10; row++) {
            for (let col = 0; col < 9; col++) {
                const piece = this.board[row][col];
                if (piece && piece.color === color && this.pieceTypes[piece.type] === 'general') {
                    return { piece, row, col };
                }
            }
        }
        return null;
    }
    
    isInCheck(color) {
        const general = this.findGeneral(color);
        if (!general) return false;
        
        const opponentColor = color === 'red' ? 'black' : 'red';
        
        for (let row = 0; row < 10; row++) {
            for (let col = 0; col < 9; col++) {
                const piece = this.board[row][col];
                if (piece && piece.color === opponentColor) {
                    const validMoves = this.getValidMoves(piece, row, col);
                    if (validMoves.some(move => move.row === general.row && move.col === general.col)) {
                        return true;
                    }
                }
            }
        }
        
        return false;
    }
    
    isCheckmate(color) {
        // 简化版本：检查是否有任何合法移动
        for (let row = 0; row < 10; row++) {
            for (let col = 0; col < 9; col++) {
                const piece = this.board[row][col];
                if (piece && piece.color === color) {
                    const validMoves = this.getValidMoves(piece, row, col);
                    if (validMoves.length > 0) {
                        return false;
                    }
                }
            }
        }
        return true;
    }
    
    updateGameInfo() {
        document.getElementById('current-player').textContent = 
            this.currentPlayer === 'red' ? '红方' : '黑方';
        
        let statusText = '进行中';
        if (this.gameStatus === 'red_wins') {
            statusText = '红方获胜';
        } else if (this.gameStatus === 'black_wins') {
            statusText = '黑方获胜';
        }
        
        document.getElementById('game-status').textContent = statusText;
    }
    
    restart() {
        this.currentPlayer = 'red';
        this.selectedPiece = null;
        this.gameStatus = 'playing';
        this.capturedPieces = { red: [], black: [] };
        this.initializeBoard();
        this.renderBoard();
        this.updateGameInfo();
        this.updateCapturedPieces();
    }
}

// 初始化游戏
document.addEventListener('DOMContentLoaded', () => {
    new ChineseChess();
});