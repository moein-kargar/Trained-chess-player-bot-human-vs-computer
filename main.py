# main.py
# Standalone Pygame chess game: human vs human (no bot).

import sys
import pygame
import pygame.freetype

from settings import WIDTH, HEIGHT, SQUARE_SIZE, FPS
from rl.game_state import GameState

from rules import is_in_check

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess - OOP Modular (Ready for RL)")
    clock = pygame.time.Clock()
    font = pygame.freetype.SysFont(None, 18)

    gs = GameState()

    running = True
    while running:
        clock.tick(FPS)

        # draw board and pieces
        gs.board_obj.draw(screen)

        # highlight valid moves
        if gs.selected and gs.board[gs.selected[0]][gs.selected[1]] and gs.board[gs.selected[0]][gs.selected[1]][0] == gs.turn:
            for rr, cc in gs.valid_moves:
                s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                s.fill((50, 205, 50, 100))
                screen.blit(s, (cc * SQUARE_SIZE, rr * SQUARE_SIZE))

        # show turn
        font.render_to(screen, (5, 5), f"Turn: {'White' if gs.turn == 'w' else 'Black'}", (0, 0, 0))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                r, c = gs.pos_to_rc(event.pos)
                if not (0 <= r < 8 and 0 <= c < 8):
                    continue
                if gs.selected is None:
                    if gs.board[r][c] != "" and gs.board[r][c][0] == gs.turn:
                        gs.selected = (r, c)
                        gs.valid_moves = gs.get_valid_moves_for(r, c)
                else:
                    if gs.selected == (r, c):
                        gs.selected = None
                        gs.valid_moves = []
                    elif (r, c) in gs.valid_moves:
                        r0, c0 = gs.selected
                        gs.make_move(r0, c0, r, c, screen)
                        gs.selected = None
                        gs.valid_moves = []

                        # check for checkmate/stalemate
                        has_any = False
                        for rr in range(8):
                            for cc in range(8):
                                if gs.board[rr][cc] != "" and gs.board[rr][cc][0] == gs.turn:
                                    if gs.get_valid_moves_for(rr, cc):
                                        has_any = True
                                        break
                            if has_any:
                                break
                        if not has_any:
                            if is_in_check(gs.board, gs.turn):
                                print("Checkmate!", "White wins" if gs.turn == 'b' else "Black wins")
                            else:
                                print("Stalemate!")
                            running = False
                    elif gs.board[r][c] != "" and gs.board[r][c][0] == gs.turn:
                        gs.selected = (r, c)
                        gs.valid_moves = gs.get_valid_moves_for(r, c)
                    else:
                        gs.selected = None
                        gs.valid_moves = []

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
