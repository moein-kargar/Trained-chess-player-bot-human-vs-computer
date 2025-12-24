# rl/rl_env.py
import numpy as np
from rules import is_in_check

from .rl_utils import action_to_index, index_to_action


class ChessEnv:
    def __init__(self, game_state):
        self.gs = game_state

    def reset(self):
        self.gs.reset()
        return self._get_obs()

    def _get_obs(self):
        b = self.gs.board
        ch_map = ["pawn", "rook", "bishop", "knight", "queen", "king"]
        obs = np.zeros((13, 8, 8), dtype=np.float32)

        for r in range(8):
            for c in range(8):
                p = b[r][c]
                if not p:
                    continue
                color = p[0]
                kind = p[1:]
                kind_idx = ch_map.index(kind)
                ch = kind_idx * 2 + (0 if color == "w" else 1)
                obs[ch, r, c] = 1.0

        obs[12, :, :] = 1.0 if self.gs.turn == "w" else 0.0
        return obs

    def legal_action_indices(self):
        legal = []
        for r in range(8):
            for c in range(8):
                piece = self.gs.board[r][c]
                if piece and piece[0] == self.gs.turn:
                    moves = self.gs.get_valid_moves_for(r, c)
                    for (r2, c2) in moves:
                        # promotion
                        if piece[1:] == "pawn" and (r2 == 0 or r2 == 7):
                            for promo in (1, 2, 3, 4):  # q,r,b,n
                                legal.append(action_to_index(r * 8 + c, r2 * 8 + c2, promo))
                        else:
                            legal.append(action_to_index(r * 8 + c, r2 * 8 + c2, 0))
        return legal

    def step(self, action_index):
        fr, to, promo = index_to_action(action_index)
        r0, c0 = divmod(fr, 8)
        r1, c1 = divmod(to, 8)

        legal = self.legal_action_indices()
        if action_index not in legal:
            return self._get_obs(), -1.0, True, {"illegal": True}

        piece = self.gs.board[r0][c0]
        self.gs.make_move(r0, c0, r1, c1, screen=None)  # RL mode: no UI

        # apply promotion choice (RL)
        if promo != 0 and piece and piece[1:] == "pawn":
            pmap = {1: "queen", 2: "rook", 3: "bishop", 4: "knight"}
            self.gs.board[r1][c1] = piece[0] + pmap[promo]

        # terminal detection
        has_any = False
        for rr in range(8):
            for cc in range(8):
                if self.gs.board[rr][cc] != "" and self.gs.board[rr][cc][0] == self.gs.turn:
                    if self.gs.get_valid_moves_for(rr, cc):
                        has_any = True
                        break
            if has_any:
                break

        if not has_any:
            if is_in_check(self.gs.board, self.gs.turn):
                return self._get_obs(), 1.0, True, {}
            return self._get_obs(), 0.5, True, {}

        return self._get_obs(), 0.0, False, {}

    def clone(self):
        return ChessEnv(self.gs.clone())
