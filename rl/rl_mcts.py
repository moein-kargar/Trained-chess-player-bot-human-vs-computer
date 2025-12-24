# rl/rl_mcts.py
import math
from collections import defaultdict

import numpy as np
import torch

from .rl_utils import ACTION_SIZE


class MCTS:
    def __init__(self, net, cpuct=1.0, n_sim=50):
        self.net = net
        self.cpuct = cpuct
        self.n_sim = n_sim

        self.P = {}  # priors: P[state][a]
        self.N = defaultdict(lambda: defaultdict(int))
        self.W = defaultdict(lambda: defaultdict(float))
        self.Q = defaultdict(lambda: defaultdict(float))

    def state_key(self, obs):
        return obs.tobytes()

    def run(self, root_env):
        root_obs = root_env._get_obs()
        root_key = self.state_key(root_obs)

        for _ in range(self.n_sim):
            env = root_env.clone()
            self._simulate(env)

        counts = np.zeros(ACTION_SIZE, dtype=np.int32)
        for a in root_env.legal_action_indices():
            counts[a] = self.N[root_key][a]
        return counts

    def _simulate(self, env):
        path = []

        while True:
            obs = env._get_obs()
            key = self.state_key(obs)
            legal = env.legal_action_indices()

            if not legal:
                value = 0.0
                break

            if key not in self.P:
                x = torch.tensor(obs, dtype=torch.float32).unsqueeze(0)
                with torch.no_grad():
                    logits, v = self.net(x)
                    probs = torch.softmax(logits, dim=-1).squeeze(0).cpu().numpy()
                    value = float(v.item())
                self.P[key] = {a: float(probs[a]) for a in legal}
                break

            total_N = sum(self.N[key][a] for a in legal) + 1
            best_a, best_score = None, -1e9
            for a in legal:
                q = self.Q[key].get(a, 0.0)
                p = self.P[key].get(a, 1e-8)
                u = q + self.cpuct * p * math.sqrt(total_N) / (1 + self.N[key][a])
                if u > best_score:
                    best_score, best_a = u, a

            path.append((key, best_a))
            env.step(best_a)

        for key, a in reversed(path):
            self.N[key][a] += 1
            self.W[key][a] += value
            self.Q[key][a] = self.W[key][a] / self.N[key][a]
            value = -value
