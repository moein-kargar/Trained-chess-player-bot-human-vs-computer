# rules.py
# Board-wide rules: in-bounds checks, attack detection, check detection

from settings import ROWS, COLS

def in_bounds(r, c):
    return 0 <= r < ROWS and 0 <= c < COLS

def attacks_square(board, r, c, attacking_color):
    """
    Returns True if a piece of color `attacking_color` attacks square (r, c).
    board: 8x8 array of strings like "wking", "bpawn", or "".
    """
    for rr in range(ROWS):
        for cc in range(COLS):
            piece = board[rr][cc]
            if not piece or piece[0] != attacking_color:
                continue
            kind = piece[1:]

            # pawn capture
            if kind == "pawn":
                direction = -1 if attacking_color == 'w' else 1
                for dc in (-1, 1):
                    ar, ac = rr + direction, cc + dc
                    if (ar, ac) == (r, c) and in_bounds(ar, ac):
                        return True

            # knight
            if kind == "knight":
                for dr, dc in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
                    ar, ac = rr + dr, cc + dc
                    if (ar, ac) == (r, c) and in_bounds(ar, ac):
                        return True

            # bishop / queen (diagonals)
            if kind in ("bishop", "queen"):
                if abs(r - rr) == abs(c - cc) and abs(r - rr) != 0:
                    step_r = (r - rr) // abs(r - rr)
                    step_c = (c - cc) // abs(c - cc)
                    pr, pc = rr + step_r, cc + step_c
                    blocked = False
                    while (pr, pc) != (r, c):
                        if board[pr][pc] != "":
                            blocked = True
                            break
                        pr += step_r
                        pc += step_c
                    if not blocked:
                        return True

            # rook / queen (files & ranks)
            if kind in ("rook", "queen"):
                # same row
                if rr == r and cc != c:
                    step = 1 if cc < c else -1
                    blocked = False
                    for x in range(cc + step, c, step):
                        if board[r][x] != "":
                            blocked = True
                            break
                    if not blocked:
                        return True
                # same column
                if cc == c and rr != r:
                    step = 1 if rr < r else -1
                    blocked = False
                    for y in range(rr + step, r, step):
                        if board[y][c] != "":
                            blocked = True
                            break
                    if not blocked:
                        return True

            # king (adjacent)
            if kind == "king":
                if max(abs(rr - r), abs(cc - c)) == 1:
                    return True
    return False

def find_king(board, color):
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] == color + "king":
                return (r, c)
    return None

def is_in_check(board, color):
    kp = find_king(board, color)
    if not kp:
        # If king missing, consider it "in check" (invalid but treat as losing)
        return True
    enemy = 'b' if color == 'w' else 'w'
    return attacks_square(board, kp[0], kp[1], enemy)
