import os
import argparse
import numpy as np
from collections import deque

from src.env.generator_env import generatorEnv
from src.env.solver_env import SolverEnv
from src.agents.dqn_agent import DQNAgent

# ------------------------------------------------------------
# helpers
# ------------------------------------------------------------

def latest_level_idx(folder: str = "custom_created") -> int:
    """Returns the highest index in data/levels/<folder>/level_XXXX.txt.
    If folder is empty, returns -1."""
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    lvl_dir = os.path.join(root, "data", "levels", folder)
    os.makedirs(lvl_dir, exist_ok=True)
    txts = sorted([f for f in os.listdir(lvl_dir) if f.startswith("level_") and f.endswith(".txt")])
    if not txts:
        return -1
    return int(txts[-1].split("_")[1].split(".")[0])


# ------------------------------------------------------------
# training loop
# ------------------------------------------------------------

def train(args):
    gen_env = generatorEnv(max_steps=args.gen_max_steps, render_mode=None)
    sol_env_template = lambda idx: SolverEnv(level_folder="custom_created", level_index=idx,
                                             max_steps=args.sol_max_steps, render_mode=None)

    # DQN Agents
    gen_agent = DQNAgent(gen_env.observation_space.shape, gen_env.action_space.n,
                         buffer_size=args.buffer_size, lr=args.lr, batch_size=args.batch,
                         epsilon_decay=args.eps_decay)
    sol_agent = DQNAgent((gen_env.observation_space.shape), 4,   # solver has same #channels but 4 actions
                         buffer_size=args.buffer_size, lr=args.lr, batch_size=args.batch,
                         epsilon_decay=args.eps_decay)

    for ep in range(1, args.episodes + 1):
        # -------- Generator phase --------
        s, info = gen_env.reset()
        ep_mem = []  # store transitions so we can add adversarial bonus at the end
        done = False
        while not done:
            a = gen_agent.act(s, info["action_mask"])
            s_next, r, term, trunc, info = gen_env.step(a)
            done = term or trunc
            ep_mem.append((s, a, r, s_next, float(done)))
            s = s_next
        # episode finished, level is saved iff generator placed FINISH
        # identify the level index just created (if any)
        lvl_idx = latest_level_idx()
        # -------- Solver phase (only if a level exists) --------
        solver_result = "NO_LEVEL"
        if lvl_idx >= 0:
            sol_env = sol_env_template(lvl_idx)
            s_sol, info_sol = sol_env.reset()
            done_sol = False
            steps_sol = 0
            while not done_sol:
                a_sol = sol_agent.act(s_sol, info_sol["action_mask"])
                s_sol_next, r_sol, term_sol, trunc_sol, info_sol = sol_env.step(a_sol)
                done_sol = term_sol or trunc_sol
                sol_agent.remember(s_sol, a_sol, r_sol, s_sol_next, float(done_sol))
                sol_agent.update()
                s_sol = s_sol_next
                steps_sol += 1
            solver_result = info_sol["result"]
        # -------- adversarial reward shaping --------
        bonus = 0.0
        if solver_result == "NO_LEVEL":
            bonus = -0.5  # generator failed to place finish
        elif solver_result == "SUCCESS":
            bonus = -1.0  # solver solved → punish generator
        else:
            bonus = +1.0  # solver failed → reward generator

        # attach bonus to last transition in memory
        s_last, a_last, r_last, s_next_last, done_last = ep_mem[-1]
        ep_mem[-1] = (s_last, a_last, r_last + bonus, s_next_last, done_last)

        # push all transitions & update gen agent
        for trans in ep_mem:
            gen_agent.remember(*trans)
            gen_agent.update()

        # -------- logging --------
        if ep % args.log_every == 0:
            print(f"Episode {ep:>5}: level={lvl_idx if lvl_idx>=0 else '–'} | solver={solver_result} | bonus={bonus:+.1f}")

        # -------- checkpoint --------
        if ep % args.save_every == 0:
            gen_agent.save(os.path.join(args.ckpt_dir, f"gen_{ep}.pth"))
            sol_agent.save(os.path.join(args.ckpt_dir, f"sol_{ep}.pth"))


# ------------------------------------------------------------
# CLI
# ------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Adversarial training: level generator vs solver")
    parser.add_argument("--episodes", type=int, default=100_000)
    parser.add_argument("--gen_max_steps", type=int, default=300)
    parser.add_argument("--sol_max_steps", type=int, default=300)
    parser.add_argument("--buffer_size", type=int, default=500_000)
    parser.add_argument("--batch", type=int, default=128)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--eps_decay", type=int, default=50_000)
    parser.add_argument("--log_every", type=int, default=100)
    parser.add_argument("--save_every", type=int, default=5_000)
    parser.add_argument("--ckpt_dir", type=str, default="checkpoints")
    args = parser.parse_args()

    os.makedirs(args.ckpt_dir, exist_ok=True)
    train(args)
