# rl/game_state.py
import sys
import pygame

from settings import WIDTH, HEIGHT, SQUARE_SIZE, FPS
from board import Board
from pieces import MoveGenerator


class GameState:
    def __init__(self):
        self.board_obj = Board()
        self.board = self.board_obj.board
        self.turn = "w"

        self.has_moved = {
            "wking": False, "bking": False,
            "wrook_k": False, "wrook_q": False,
            "brook_k": False, "brook_q": False
        }

        self.en_passant_target = None
        self.selected = None
        self.valid_moves = []
        self.movegen = MoveGenerator()

    def reset(self):
        self.board_obj.reset()
        self.board = self.board_obj.board
        self.turn = "w"
        for k in self.has_moved:
            self.has_moved[k] = False
        self.en_passant_target = None
        self.selected = None
        self.valid_moves = []

    def pos_to_rc(self, pos):
        x, y = pos
        return y // SQUARE_SIZE, x // SQUARE_SIZE

    def get_valid_moves_for(self, r, c):
        return self.movegen.legal_moves_safe(self.board, r, c, self.en_passant_target, self.has_moved)

    def make_move(self, r0, c0, r, c, screen=None):
        piece = self.board[r0][c0]
        if not piece:
            return False

        color = piece[0]
        kind = piece[1:]

        # en passant capture
        if kind == "pawn" and self.en_passant_target and (r, c) == self.en_passant_target and c != c0 and self.board[r][c] == "":
            direction = -1 if color == "w" else 1
            captured_r = r - direction
            self.board[captured_r][c] = ""

        # castling rook move
        if kind == "king" and abs(c - c0) == 2:
            if c == 6:  # king side
                self.board[r][5] = self.board[r][7]
                self.board[r][7] = ""
                if color == "w":
                    self.has_moved["wrook_k"] = True
                else:
                    self.has_moved["brook_k"] = True
            elif c == 2:  # queen side
                self.board[r][3] = self.board[r][0]
                self.board[r][0] = ""
                if color == "w":
                    self.has_moved["wrook_q"] = True
                else:
                    self.has_moved["brook_q"] = True

        # move piece
        self.board[r][c] = self.board[r0][c0]
        self.board[r0][c0] = ""

        # promotion
        if kind == "pawn" and ((color == "w" and r == 0) or (color == "b" and r == 7)):
            choice = "queen"
            if screen is not None:
                choice = self.show_promotion_menu(screen, color) or "queen"
            self.board[r][c] = color + choice

        # update has_moved
        if kind == "king":
            self.has_moved[color + "king"] = True
        elif kind == "rook":
            if color == "w":
                if r0 == 7 and c0 == 0:
                    self.has_moved["wrook_q"] = True
                if r0 == 7 and c0 == 7:
                    self.has_moved["wrook_k"] = True
            else:
                if r0 == 0 and c0 == 0:
                    self.has_moved["brook_q"] = True
                if r0 == 0 and c0 == 7:
                    self.has_moved["brook_k"] = True

        # update en_passant_target
        if kind == "pawn" and abs(r - r0) == 2:
            self.en_passant_target = ((r + r0) // 2, c)
        else:
            self.en_passant_target = None

        # switch turn
        self.turn = "b" if self.turn == "w" else "w"
        return True

    def show_promotion_menu(self, screen, color):
        opts = ["queen", "rook", "bishop", "knight"]
        menu_w = SQUARE_SIZE * 4
        menu_h = SQUARE_SIZE
        menu_x = (WIDTH - menu_w) // 2
        menu_y = (HEIGHT - menu_h) // 2
        clock_local = pygame.time.Clock()

        while True:
            clock_local.tick(FPS)
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            pygame.draw.rect(screen, (220, 220, 220), (menu_x, menu_y, menu_w, menu_h))

            rects = []
            for i, opt in enumerate(opts):
                x = menu_x + i * SQUARE_SIZE
                y = menu_y
                rect = pygame.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE)
                rects.append((rect, opt))
                key = color + opt
                img = self.board_obj.piece_images.get(key)
                if img:
                    screen.blit(img, (x, y))
                else:
                    pygame.draw.rect(screen, (100, 100, 100), rect)

            pygame.display.flip()

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    mx, my = ev.pos
                    for rect, opt in rects:
                        if rect.collidepoint(mx, my):
                            return opt
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    return None

    def clone(self):
        # lightweight clone for MCTS (no image loading)
        new = GameState.__new__(GameState)
        new.board_obj = None
        new.board = [row[:] for row in self.board]
        new.turn = self.turn
        new.has_moved = self.has_moved.copy()
        new.en_passant_target = self.en_passant_target
        new.selected = None
        new.valid_moves = []
        new.movegen = self.movegen
        return new
