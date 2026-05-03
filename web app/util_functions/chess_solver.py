import copy
from typing import List, Tuple, Optional, Dict

class ChessBoard:
    def __init__(self):
        # 8x8 board representation: uppercase = white, lowercase = black
        # Empty squares = '.'
        self.board = [
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        ]
        
        # Piece values for evaluation
        self.piece_values = {
            'p': -1, 'n': -3, 'b': -3, 'r': -5, 'q': -9, 'k': -100,
            'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 100,
            '.': 0
        }
        
        # Position bonus tables for pieces
        self.pawn_table = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [5, 5, 5, 5, 5, 5, 5, 5],
            [1, 1, 2, 3, 3, 2, 1, 1],
            [0, 0, 1, 2, 2, 1, 0, 0],
            [0, 0, 0, 2, 2, 0, 0, 0],
            [0, 0, -1, 0, 0, -1, 0, 0],
            [0, 1, 1, -2, -2, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
        
        self.knight_table = [
            [-5, -4, -3, -3, -3, -3, -4, -5],
            [-4, -2, 0, 0, 0, 0, -2, -4],
            [-3, 0, 1, 1, 1, 1, 0, -3],
            [-3, 0, 1, 1, 1, 1, 0, -3],
            [-3, 0, 1, 1, 1, 1, 0, -3],
            [-3, 0, 1, 1, 1, 1, 0, -3],
            [-4, -2, 0, 1, 1, 0, -2, -4],
            [-5, -4, -3, -3, -3, -3, -4, -5]
        ]
    
    def is_valid_pos(self, row: int, col: int) :
        return 0 <= row < 8 and 0 <= col < 8
    
    def is_white_piece(self, piece: str) :
        return piece.isupper()
    
    def is_black_piece(self, piece: str):
        return piece.islower()
    
    def get_piece_moves(self, row: int, col: int):
        """Get all valid moves for a piece at given position"""
        piece = self.board[row][col]
        if piece == '.':
            return []
        
        moves = []
        piece_type = piece.lower()
        
        if piece_type == 'p':
            moves = self._get_pawn_moves(row, col, self.is_white_piece(piece))
        elif piece_type == 'r':
            moves = self._get_rook_moves(row, col)
        elif piece_type == 'n':
            moves = self._get_knight_moves(row, col)
        elif piece_type == 'b':
            moves = self._get_bishop_moves(row, col)
        elif piece_type == 'q':
            moves = self._get_queen_moves(row, col)
        elif piece_type == 'k':
            moves = self._get_king_moves(row, col)
        
        # Filter out moves that would capture own pieces
        valid_moves = []
        for new_row, new_col in moves:
            if self.is_valid_pos(new_row, new_col):
                target = self.board[new_row][new_col]
                if target == '.' or (self.is_white_piece(piece) != self.is_white_piece(target)):
                    valid_moves.append((new_row, new_col))
        
        return valid_moves
    
    def _get_pawn_moves(self, row: int, col: int, is_white: bool):
        moves = []
        direction = -1 if is_white else 1
        start_row = 6 if is_white else 1
        
        # Forward move
        new_row = row + direction
        if self.is_valid_pos(new_row, col) and self.board[new_row][col] == '.':
            moves.append((new_row, col))
            
            # Double move from starting position
            if row == start_row and self.board[new_row + direction][col] == '.':
                moves.append((new_row + direction, col))
        
        # Captures
        for dc in [-1, 1]:
            new_row, new_col = row + direction, col + dc
            if self.is_valid_pos(new_row, new_col):
                target = self.board[new_row][new_col]
                if target != '.' and (is_white != self.is_white_piece(target)):
                    moves.append((new_row, new_col))
        
        return moves
    
    def _get_rook_moves(self, row: int, col: int):
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = row + i * dr, col + i * dc
                if not self.is_valid_pos(new_row, new_col):
                    break
                
                target = self.board[new_row][new_col]
                if target == '.':
                    moves.append((new_row, new_col))
                else:
                    moves.append((new_row, new_col))  # Capture
                    break
        
        return moves
    
    def _get_knight_moves(self, row: int, col: int):
        moves = []
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1)]
        
        for dr, dc in knight_moves:
            new_row, new_col = row + dr, col + dc
            if self.is_valid_pos(new_row, new_col):
                moves.append((new_row, new_col))
        
        return moves
    
    def _get_bishop_moves(self, row: int, col: int):
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = row + i * dr, col + i * dc
                if not self.is_valid_pos(new_row, new_col):
                    break
                
                target = self.board[new_row][new_col]
                if target == '.':
                    moves.append((new_row, new_col))
                else:
                    moves.append((new_row, new_col))  # Capture
                    break
        
        return moves
    
    def _get_queen_moves(self, row: int, col: int):
        return self._get_rook_moves(row, col) + self._get_bishop_moves(row, col)
    
    def _get_king_moves(self, row: int, col: int):
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0),
                     (1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if self.is_valid_pos(new_row, new_col):
                moves.append((new_row, new_col))
        
        return moves
    
    def make_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]):
        """Create a new board with the move applied"""
        new_board = copy.deepcopy(self)
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        new_board.board[to_row][to_col] = new_board.board[from_row][from_col]
        new_board.board[from_row][from_col] = '.'
        
        return new_board
    
    def get_all_moves(self, is_white_turn: bool):
        """Get all possible moves for the current player"""
        moves = []
        
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece != '.' and (is_white_turn == self.is_white_piece(piece)):
                    piece_moves = self.get_piece_moves(row, col)
                    for to_pos in piece_moves:
                        moves.append(((row, col), to_pos))
        
        return moves
    
    def evaluate(self):
        """Evaluate the board position"""
        score = 0
        
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece != '.':
                    # Material value
                    score += self.piece_values[piece]
                    
                    # Positional bonuses
                    piece_type = piece.lower()
                    if piece_type == 'p':
                        if self.is_white_piece(piece):
                            score += self.pawn_table[row][col] * 0.1
                        else:
                            score -= self.pawn_table[7-row][col] * 0.1
                    elif piece_type == 'n':
                        if self.is_white_piece(piece):
                            score += self.knight_table[row][col] * 0.1
                        else:
                            score -= self.knight_table[7-row][col] * 0.1
        
        return score
    
    def is_in_check(self, is_white_king: bool) :
        """Check if the king is in check"""
        # Find king position
        king = 'K' if is_white_king else 'k'
        king_pos = None
        
        for row in range(8):
            for col in range(8):
                if self.board[row][col] == king:
                    king_pos = (row, col)
                    break
            if king_pos:
                break
        
        if not king_pos:
            return False
        
        # Check if any opponent piece can attack the king
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece != '.' and (is_white_king != self.is_white_piece(piece)):
                    moves = self.get_piece_moves(row, col)
                    if king_pos in moves:
                        return True
        
        return False
    
    def pos_to_notation(self, pos: Tuple[int, int]):
        """Convert position to chess notation"""
        row, col = pos
        return chr(ord('a') + col) + str(8 - row)
    
    def print_board(self):
        """Print the board in a readable format"""
        print("  a b c d e f g h")
        for i, row in enumerate(self.board):
            print(f"{8-i} {' '.join(row)} {8-i}")
        print("  a b c d e f g h")


def minimax(board: ChessBoard, depth: int, alpha: float, beta: float, 
           is_maximizing: bool, is_white_turn: bool):
    """Minimax algorithm with alpha-beta pruning"""
    
    if depth == 0:
        return board.evaluate(), None
    
    moves = board.get_all_moves(is_white_turn)
    
    if not moves:  # No legal moves (checkmate or stalemate)
        if board.is_in_check(is_white_turn):
            return -1000 if is_white_turn else 1000, None  # Checkmate
        else:
            return 0, None  # Stalemate
    
    best_move = None
    
    if is_maximizing:
        max_eval = float('-inf')
        for move in moves:
            from_pos, to_pos = move
            new_board = board.make_move(from_pos, to_pos)
            
            # Skip moves that leave king in check
            if new_board.is_in_check(is_white_turn):
                continue
            
            eval_score, _ = minimax(new_board, depth - 1, alpha, beta, False, not is_white_turn)
            
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break  # Alpha-beta pruning
        
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in moves:
            from_pos, to_pos = move
            new_board = board.make_move(from_pos, to_pos)
            
            # Skip moves that leave king in check
            if new_board.is_in_check(is_white_turn):
                continue
            
            eval_score, _ = minimax(new_board, depth - 1, alpha, beta, True, not is_white_turn)
            
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            
            beta = min(beta, eval_score)
            if beta <= alpha:
                break  # Alpha-beta pruning
        
        return min_eval, best_move


def predict_best_move(board: ChessBoard, is_white_turn: bool, depth: int = 3):
    """
    Predict the best move for the current position
    
    Args:
        board: ChessBoard object representing current position
        is_white_turn: True if it's white's turn, False for black
        depth: Search depth (higher = stronger but slower)
    
    Returns:
        Tuple of (from_notation, to_notation) e.g. ("e2", "e4")
    """
    
    _, best_move = minimax(board, depth, float('-inf'), float('inf'), 
                          is_white_turn, is_white_turn)
    
    if best_move is None:
        # No legal moves found
        return None, None
    
    from_pos, to_pos = best_move
    from_notation = board.pos_to_notation(from_pos)
    to_notation = board.pos_to_notation(to_pos)
    
    return from_notation, to_notation


#Example usage and testing
if __name__ == "__main__":
    # Create a new chess board
    chess_board = ChessBoard()
    
    print("Initial board position:")
    chess_board.print_board()

    chess_board.board = [
        ['r', '.', 'b', 'q', 'k', '.', '.', 'r'],
        ['p', 'p', 'n', 'p', '.', 'p', 'p', 'p'],
        ['.', '.', 'p', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', 'p', '.', '.', '.'],
        ['.', '.', 'B', 'P', 'P', '.', '.', '.'],
        ['.', '.', 'N', '.', '.', 'N', '.', '.'],
        ['P', 'P', 'P', '.', '.', 'P', 'P', 'P'],
        ['R', '.', '.', 'Q', 'K', '.', '.', 'R']
    ]
    
    # Get best move for white (opening move)
    from_move, to_move = predict_best_move(chess_board, is_white_turn=True, depth=3)
    
    
    if from_move and to_move:
        print(f"\nBest move for White: {from_move} -> {to_move}")
        
        # Make the move
        from_pos = (8 - int(from_move[1]), ord(from_move[0]) - ord('a'))
        to_pos = (8 - int(to_move[1]), ord(to_move[0]) - ord('a'))
        chess_board = chess_board.make_move(from_pos, to_pos)
        
        print("\nBoard after white's move:")
        chess_board.print_board()
        
        # Get best move for black
        from_move, to_move = predict_best_move(chess_board, is_white_turn=False, depth=3)
        
        if from_move and to_move:
            print(f"\nBest move for Black: {from_move} -> {to_move}")
    else:
        print("No legal moves found!")
