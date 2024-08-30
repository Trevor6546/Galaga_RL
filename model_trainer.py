import argparse
import random
import gymnasium as gym
import numpy as np
from gymnasium.wrappers.time_limit import TimeLimit
import retro

class Frameskip(gym.Wrapper):
    def __init__(self, env, skip=4):
        super().__init__(env)
        self._skip = skip
    
    def reset(self):
        return self.env.reset()

    def step(self, act):
        cum_reward = 0.0
        terminated, truncated = False, False
        for i in range(self._skip):
            obs, reward, terminated, truncated, info = self.env.step(act)
            cum_reward += reward
            if terminated or truncated:
                break

        return obs, cum_reward, terminated, truncated, info

class Node:
    def __init__(self, value=-np.inf, children=None):
        self.value = value
        self.visits = 0
        if children is None:
            self.children = {}
        else:
            self.children = children
        
    def __repr__(self):
        return "<Node value=%f visits=%d len(children)=%d>" % (self.value, self.visits, len(self.children))
    
def select_actions(root, action_space, max_episode_steps):
    node = root
    moves = []
    steps = 0
    while steps < max_episode_steps:
        if node is None:
            move = action_space.sample()
        else:
            epsilon = 0.005 / np.log(node.visits+2)
            if random.random() < epsilon:
                move = action_space.sample()
            else:
                move_value = {}
                for move in range(action_space.n):
                    if node is not None and move in node.children:
                        move_value[move] = node.children[move].value
                    else:
                        move_value[move] = -np.inf
                best_value = max(move_value.values())
                best_moves = [move for move, value in move_value.items() if value == best_value]
                move = random.choice(best_moves)
            if move in node.children:
                node = node.children[move]
            else:
                node = None
        moves.append(move)
        steps += 1
    return moves

def rollout(env, moves):
    cum_reward = 0
    env.reset()
    steps = 0
    for move in moves:
        _obs, reward, terminated, truncated, _info = env.step(move)
        steps += 1
        cum_reward += reward
        if terminated or truncated:
            break
    
    return steps, cum_reward

def update_tree(root, executed_acts, cum_reward):
    root.value = max(cum_reward, root.value)
    root.visits += 1
    new_nodes = 0
    
    node = root
    for step, move in enumerate(executed_acts):
        if move not in node.children:
            node.children[move] = Node()
            new_nodes += 1
        node = node.children[move]
        node.value = max(cum_reward, node.value)
        node.visits += 1
    return new_nodes

class Brute:
    def __init__(self, env, max_episode_steps):
        self.node_count = 1
        self._root = Node()
        self._env = env
        self._max_episodes_steps = max_episode_steps

    def run(self):
        moves = select_actions(self._root, self._env.action_space, self._max_episodes_steps)
        steps, cum_rewards = rollout(self._env, moves)
        executed_acts = moves[:steps]
        self.node_count += update_tree(self._root, executed_acts, cum_rewards)
        return executed_acts, cum_rewards
    

def brute_retro(game, max_episodes_steps=4500, timestep_limit=100000, state=retro.State.DEFAULT, scenario = None):
    env = retro.make(game, state, use_restricted_actions=retro.Actions.DISCRETE, scenario=scenario)
    env = Frameskip(env)
    env = TimeLimit(env, max_episodes_steps=max_episodes_steps)

    brute = Brute(env, max_episodes_steps=max_episodes_steps)
    timesteps = 0
    best_reward = float("-inf")
    while True:
        moves, reward = brute.run()
        timesteps += len(moves)

        if reward > best_reward:
            print(f"new best reward {best_rew} => {reward}")
            best_rew = reward
            env.unwrapped.record_move("best.bk2")
            env.reset()
            for move in moves:
                env.step(move)
            env.unwrapped.stop_record()
        
        print("Current Timestep: ",timesteps)
        print("Difference From Best: ", (best_rew))

        if timesteps > timestep_limit:
            print("timestep limit exceeded")
            break
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--game", default="Airstriker-Genesis")
    parser.add_argument("--state", default=retro.State.DEFAULT)
    parser.add_argument("--scenario", default=None)
    args = parser.parse_args()
    brute_retro(game=args.game, state=args.state, scenario=args.scenario)

if __name__ == "__main__":
    main()