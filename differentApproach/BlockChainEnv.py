import gym
from gym import spaces
import numpy as np

class BitcoinEnv(gym.Env):
    def __init__(self):
        # Define the observation space and action space
        self.observation_space = spaces.Box(low=0, high=1, shape=(4,))
        self.action_space = spaces.Discrete(2)
        # Define the initial state
        self.block_size = 0
        self.transactions = []
        # Define the target utilization rate
        self.target_utilization_rate = 0.8
        # Define the penalty for low utilization rate
        self.utilization_penalty = -10
        # Define the penalty for single transactions
        self.single_transaction_penalty = -5
    def step(self, action):
        # Create a block or wait for more transactions
        if action == 0:
            # Create a block with the current set of transactions
            block_size = self.block_size + sum([t["size"] for t in self.transactions])
            utilization_rate = block_size / 1000
            total_fees = sum([t["fee"] for t in self.transactions])
            # Calculate the reward
            if utilization_rate >= self.target_utilization_rate:
                # The utilization rate is above the target
                reward = total_fees
            else:
                # The utilization rate is below the target
                reward = total_fees + self.utilization_penalty * (self.target_utilization_rate - utilization_rate)
            if len(self.transactions) == 1:
                # There is only one transaction in the block
                reward += self.single_transaction_penalty
            # Reset the state to wait for new transactions
            self.block_size = 0
            self.transactions = []
        else:
            # Wait for more transactions
            reward = 0
        # Update the state
        state = np.array([len(self.transactions) / 10, self.block_size / 1000, self.target_utilization_rate, reward])
        return state, reward, False, {}
    def reset(self):
        # Reset the state to wait for new transactions
        self.block_size = 0
        self.transactions = []
        state = np.array([0, 0, self.target_utilization_rate, 0])
        return state
    def add_transaction(self, fee, size):
        # Add a new transaction to the current set of transactions
        self.transactions.append({"fee": fee, "size": size})
        self.block_size += size
