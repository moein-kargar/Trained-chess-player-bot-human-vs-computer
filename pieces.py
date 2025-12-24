# pieces.py
# Move generation (including en passant and castling).
# Final king-safety is handled via rules.is_in_check.

from settings import ROWS, COLS
from rules import in_bounds, attacks_square, is_in_check

def is_empty(board, r, c):
    return board[r][c] == ""

class MoveGenerator:
    def __init__(self):
        # Castling flags are in GameState.has_moved
        pass

    def legal_moves(self, board, r, c, en_passant_target, has_moved):
        """
        Returns a list of (r2, c2) target squares for the piece on (r, c),
        without ensuring the king isn't left in check.
        """
        piece = board[r][c]
        if not piece:
            return []
        color, kind = piece[0], piece[1:]
        moves = []

        if kind == "pawn":
            direction = -1 if color == 'w' else 1
            start_row = 6 if color == 'w' else 1
            # one-step forward
            if in_bounds(r + direction, c) and is_empty(board, r + direction, c):
                moves.append((r + direction, c))
                # two-step from start
                if r == start_row and is_empty(board, r + 2 * direction, c):
                    moves.append((r + 2 * direction, c))
            # normal captures
            for dc in (-1, 1):
                nr, nc = r + direction, c + dc
                if in_bounds(nr, nc) and board[nr][nc] and board[nr][nc][0] != color:
                    moves.append((nr, nc))
            # en passant
            if en_passant_target:
                er, ec = en_passant_target
                for dc in (-1, 1):
                    if (r + direction, c + dc) == (er, ec):
                        adj_r, adj_c = r, c + dc
                        if in_bounds(adj_r, adj_c) and board[adj_r][adj_c] and board[adj_r][adj_c][0] != color and board[adj_r][adj_c][1:] == "pawn":
                            moves.append((er, ec))

        elif kind == "rook":
            dirs = [(1,0),(-1,0),(0,1),(0,-1)]
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                while in_bounds(nr, nc):
                    if is_empty(board, nr, nc):
                        moves.append((nr, nc))
                    else:
                        if board[nr][nc][0] != color:
                            moves.append((nr, nc))
                        break
                    nr += dr
                    nc += dc

        elif kind == "bishop":
            dirs = [(1,1),(1,-1),(-1,1),(-1,-1)]
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                while in_bounds(nr, nc):
                    if is_empty(board, nr, nc):
                        moves.append((nr, nc))
                    else:
                        if board[nr][nc][0] != color:
                            moves.append((nr, nc))
                        break
                    nr += dr
                    nc += dc

        elif kind == "queen":
            dirs = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                while in_bounds(nr, nc):
                    if is_empty(board, nr, nc):
                        moves.append((nr, nc))
                    else:
                        if board[nr][nc][0] != color:
                            moves.append((nr, nc))
                        break
                    nr += dr
                    nc += dc

        elif kind == "knight":
            candidates = [
                (r + 2, c + 1), (r + 2, c - 1),
                (r - 2, c + 1), (r - 2, c - 1),
                (r + 1, c + 2), (r + 1, c - 2),
                (r - 1, c + 2), (r - 1, c - 2),
            ]
            for nr, nc in candidates:
                if in_bounds(nr, nc) and (is_empty(board, nr, nc) or board[nr][nc][0] != color):
                    moves.append((nr, nc))

        elif kind == "king":
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if in_bounds(nr, nc) and (is_empty(board, nr, nc) or board[nr][nc][0] != color):
                        moves.append((nr, nc))

            # castling (needs has_moved + attacks_square)
            enemy = 'b' if color == 'w' else 'w'
            row = 7 if color == 'w' else 0
            if r == row and c == 4 and not has_moved.get(color + 'king', True):
                rook_name = ('wrook' if color == 'w' else 'brook')
                # king side
                if board[row][7] == rook_name and not has_moved.get(color + 'rook_k', True):
                    if board[row][5] == "" and board[row][6] == "":
                        if not attacks_square(board, row, 4, enemy) and not attacks_square(board, row, 5, enemy) and not attacks_square(board, row, 6, enemy):
                            moves.append((row, 6))
                # queen side
                if board[row][0] == rook_name and not has_moved.get(color + 'rook_q', True):
                    if board[row][1] == "" and board[row][2] == "" and board[row][3] == "":
                        if not attacks_square(board, row, 4, enemy) and not attacks_square(board, row, 3, enemy) and not attacks_square(board, row, 2, enemy):
                            moves.append((row, 2))

        return moves

    def legal_moves_safe(self, board, r, c, en_passant_target, has_moved):
        """
        Returns only moves that do not leave own king in check.
        """
        moves = self.legal_moves(board, r, c, en_passant_target, has_moved)
        safe = []
        piece = board[r][c]
        if not piece:
            return safe
        color = piece[0]

        for (r2, c2) in moves:
            temp = [row[:] for row in board]
            # en passant capture
            if piece[1:] == "pawn" and en_passant_target and (r2, c2) == en_passant_target and c2 != c and temp[r][c2] == "":
                direction = -1 if color == 'w' else 1
                temp[r2 - direction][c2] = ""
            temp[r2][c2] = temp[r][c]
            temp[r][c] = ""
            # castling: move rook too
            if piece[1:] == "king" and abs(c2 - c) == 2:
                if c2 == 6:
                    temp[r][5] = temp[r][7]
                    temp[r][7] = ""
                elif c2 == 2:
                    temp[r][3] = temp[r][0]
                    temp[r][0] = ""
            if not is_in_check(temp, color):
                safe.append((r2, c2))
        return safe
