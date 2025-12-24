# rl/rl_train.py
import random
from collections import deque

import numpy as np
import torch
import torch.nn.functional as F
import torch.optim as optim

from .rl_net import ChessNet
from .rl_env import ChessEnv
from .rl_mcts import MCTS
from .game_state import GameState


def self_play_episode(net, mcts_sim=25):
    gs = GameState()
    env = ChessEnv(gs)
    mcts = MCTS(net, n_sim=mcts_sim)

    states, policies = [], []
    outcome = 0.0

    while True:
        obs = env._get_obs()
        legal = env.legal_action_indices()
        if not legal:
            break

        counts = mcts.run(env)
        policy = counts.astype(np.float32)
        s = policy.sum()
        if s > 0:
            policy /= s
        else:
            policy = np.zeros_like(policy)
            for a in legal:
                policy[a] = 1.0 / len(legal)

        action = int(np.random.choice(len(policy), p=policy))
        if action not in legal:
            action = random.choice(legal)

        env.step(action)

        states.append(obs)
        policies.append(policy)

        if not env.legal_action_indices():
            outcome = 1.0
            break

    return [(s, p, outcome) for s, p in zip(states, policies)]


def train_loop(num_iters=50, games_per_iter=5):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    net = ChessNet().to(device)
    optimizer = optim.Adam(net.parameters(), lr=1e-3)

    replay = deque(maxlen=10000)

    for it in range(num_iters):
        for _ in range(games_per_iter):
            replay.extend(self_play_episode(net, mcts_sim=25))

        if len(replay) < 100:
            print(f"Iter {it}: replay={len(replay)} (not enough yet)")
            continue

        for _ in range(5):
            batch = random.sample(replay, min(64, len(replay)))
            states = np.stack([b[0] for b in batch])
            pis = np.stack([b[1] for b in batch])
            zs = np.array([b[2] for b in batch], dtype=np.float32)

            x = torch.tensor(states, dtype=torch.float32, device=device)
            target_p = torch.tensor(pis, dtype=torch.float32, device=device)
            target_v = torch.tensor(zs, dtype=torch.float32, device=device)

            logits, v = net(x)
            loss_p = -(target_p * torch.log_softmax(logits, dim=-1)).sum(dim=1).mean()
            loss_v = F.mse_loss(v, target_v)
            loss = loss_p + loss_v

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        print(f"Iteration {it} finished. Replay size: {len(replay)}")
