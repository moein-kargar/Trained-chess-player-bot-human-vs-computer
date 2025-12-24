# board.py
# Holds and draws the board using pygame.

import os
import pygame
from settings import WIDTH, HEIGHT, ROWS, COLS, SQUARE_SIZE, LIGHT, DARK, WHITE_FOLDER, BLACK_FOLDER

PIECE_NAMES = ["king", "queen", "rook", "bishop", "knight", "pawn"]

class Board:
    def __init__(self):
        # 8x8 array of strings like "wking", "bpawn", or "".
        self.initial_board = [
            ["brook", "bknight", "bbishop", "bqueen", "bking", "bbishop", "bknight", "brook"],
            ["bpawn"] * 8,
            [""] * 8,
            [""] * 8,
            [""] * 8,
            [""] * 8,
            ["wpawn"] * 8,
            ["wrook", "wknight", "wbishop", "wqueen", "wking", "wbishop", "wknight", "wrook"],
        ]
        self.board = [row[:] for row in self.initial_board]
        self.piece_images = {}
        self.load_images()

    def load_images(self):
        def load_and_scale(path):
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, (SQUARE_SIZE, SQUARE_SIZE))

        for name in PIECE_NAMES:
            w_path = os.path.join(WHITE_FOLDER, f"{name}.png")
            b_path = os.path.join(BLACK_FOLDER, f"{name}.png")
            try:
                self.piece_images["w" + name] = load_and_scale(w_path)
            except Exception as e:
                print("Warning: can't load", w_path, e)
            try:
                self.piece_images["b" + name] = load_and_scale(b_path)
            except Exception as e:
                print("Warning: can't load", b_path, e)

    def reset(self):
        self.board = [row[:] for row in self.initial_board]

    def get(self, r, c):
        return self.board[r][c]

    def set(self, r, c, val):
        self.board[r][c] = val

    def draw(self, screen):
        # draw squares
        for r in range(ROWS):
            for c in range(COLS):
                color = LIGHT if (r + c) % 2 == 0 else DARK
                pygame.draw.rect(screen, color, (c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        # draw pieces
        for r in range(ROWS):
            for c in range(COLS):
                p = self.board[r][c]
                if p:
                    img = self.piece_images.get(p)
                    if img:
                        screen.blit(img, (c * SQUARE_SIZE, r * SQUARE_SIZE))
                    else:
                        pygame.draw.rect(screen, (180, 180, 180),
                                         (c * SQUARE_SIZE + 8, r * SQUARE_SIZE + 8,
                                          SQUARE_SIZE - 16, SQUARE_SIZE - 16))

    def copy_board(self):
        return [row[:] for row in self.board]
