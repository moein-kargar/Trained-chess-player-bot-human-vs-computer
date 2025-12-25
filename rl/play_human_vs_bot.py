# rl/play_human_vs_bot.py
import pygame
import pygame.freetype
import torch


from settings import WIDTH, HEIGHT, FPS, SQUARE_SIZE
from rules import is_in_check

from .game_state import GameState
from .rl_env import ChessEnv
from .rl_net import ChessNet
from .rl_mcts import MCTS


def play_human_vs_bot(model_path=None, mcts_sim=50):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Human vs Bot Chess")
    clock = pygame.time.Clock()
    font = pygame.freetype.SysFont(None, 18)

    gs = GameState()          # your custom board-based GameState (NOT python-chess)
    env = ChessEnv(gs)

    net = ChessNet()
    if model_path is not None:
        net.load_state_dict(torch.load(model_path, map_location="cpu"))
    net.eval()

    mcts = MCTS(net, n_sim=mcts_sim)

    human_color = "w"   # human is white
    running = True

    while running:
        clock.tick(FPS)

        # draw
        gs.board_obj.draw(screen)

        # highlight moves
        if gs.selected and gs.board[gs.selected[0]][gs.selected[1]] and gs.board[gs.selected[0]][gs.selected[1]][0] == gs.turn:
            for rr, cc in gs.valid_moves:
                s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                s.fill((50, 205, 50, 100))
                screen.blit(s, (cc * SQUARE_SIZE, rr * SQUARE_SIZE))

        font.render_to(screen, (5, 5), f"Turn: {'White' if gs.turn=='w' else 'Black'}", (0, 0, 0))
        pygame.display.flip()

        # human input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and gs.turn == human_color:
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
                        gs.make_move(r0, c0, r, c, screen)  # promotion UI enabled for human
                        gs.selected = None
                        gs.valid_moves = []
                    elif gs.board[r][c] != "" and gs.board[r][c][0] == gs.turn:
                        gs.selected = (r, c)
                        gs.valid_moves = gs.get_valid_moves_for(r, c)
                    else:
                        gs.selected = None
                        gs.valid_moves = []

        if not running:
            break

        # bot move
        if gs.turn != human_color:
            legal = env.legal_action_indices()
            if not legal:
                running = False
                break

            counts = mcts.run(env)
            best_action = max(legal, key=lambda a: counts[a])
            env.step(best_action)

        # game over check
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
                print("Checkmate!", "White wins" if gs.turn == "b" else "Black wins")
            else:
                print("Stalemate!")
            running = False

    pygame.quit()


if __name__ == "__main__":
    play_human_vs_bot()
