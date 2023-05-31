import gym
from gym import spaces
import hashlib
import datetime
import random
import time
import numpy as np


class MerkleTree:
    def __init__(self, data):
        self.data = data
        self.root = self._build_tree(self.data)

    def _build_tree(self, data):
        if len(data) == 1:
            return data[0]

        if len(data) % 2 != 0:  # Duplicate the last transaction if the number is odd
            data.append(data[-1])

        next_level = []
        for i in range(0, len(data), 2):
            current_hash = self._hash_pair(data[i], data[i + 1])
            next_level.append(current_hash)

        return self._build_tree(next_level)

    def _hash_pair(self, left, right):
        return hashlib.sha256((left + right).encode()).hexdigest()


class Transaction:
    def __init__(self, timestamp, data, block_size):
        self.timestamp = timestamp
        self.data = data
        self.block_size = block_size

    def calculate_hash(self):
        data_string = str(self.timestamp) + str(self.data) + str(self.block_size)
        return hashlib.sha256(data_string.encode()).hexdigest()


class Block:
    def __init__(self, timestamp, data, previous_hash, block_size, waiting_time):
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.block_size = block_size
        self.merkle_root = self.calculate_merkle_root()
        self.hash = self.calculate_hash()
        self.average_waiting_time = waiting_time

    def calculate_merkle_root(self):
        transaction_hashes = [transaction.calculate_hash() for transaction in self.data]
        merkle_tree = MerkleTree(transaction_hashes)
        return merkle_tree.root

    def calculate_hash(self):
        data_string = str(self.timestamp) + str(self.merkle_root) + str(self.previous_hash) + str(self.block_size)
        return hashlib.sha256(data_string.encode()).hexdigest()


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.min_block_size = 1000  # 1 MB = 1000 KB
        self.pending_transactions = []
        self.current_block_size = 0
        self.waiting_times = []

    def create_genesis_block(self):
        transaction = Transaction(datetime.datetime.now(), "Genesis Block", 1)
        return Block(datetime.datetime.now(), [transaction], "0", 1, 0)

    def get_latest_block(self):
        return self.chain[-1]

    def add_transaction(self, transaction, should_mine=False):
        self.pending_transactions.append(transaction)
        self.current_block_size += transaction.block_size

        len_of_transactions = len(self.pending_transactions)

        if should_mine:
            print("Block created with size:---------------------------- ", self.current_block_size, " ----- ", len_of_transactions)
            self.mine_block()
        else:
            waiting_time = (time.time_ns() - transaction.timestamp)
            self.waiting_times.append(waiting_time)
        return len_of_transactions, self.current_block_size

    def get_all_pending_transactions(self):
        return self.pending_transactions

    def mine_block(self):
        timestamp = time.time_ns()
        data = self.pending_transactions
        new_block_size = 0
        waiting_time = 0
        average_waiting_time = 0
        # Calculate new block size
        if len(data) > 0:
            for transaction in data:
                new_block_size += transaction.block_size
        for transaction in data:
            waiting_time += (timestamp - transaction.timestamp)

        # Average waiting time
        if len(data) > 0:
            average_waiting_time = waiting_time / len(data)
        print("Block info: ", new_block_size, " ----- ", new_block_size, " ----- ", average_waiting_time, " ----- ", len(data))
        new_block = Block(timestamp, data, self.get_latest_block().hash, new_block_size, average_waiting_time)
        self.add_block(new_block)
        self.pending_transactions = []
        self.current_block_size = 0

    def add_block(self, new_block):
        new_block.previous_hash = self.get_latest_block().hash
        new_block.hash = new_block.calculate_hash()
        self.chain.append(new_block)

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.hash != current_block.calculate_hash():
                return False

            if current_block.previous_hash != previous_block.hash:
                return False

        return True


def normalize_array(arr):
    min_val = np.min(arr)
    max_val = np.max(arr)
    normalized_arr = (arr - min_val) / (max_val - min_val)
    return normalized_arr


class BlockchainCustomEnv(gym.Env):
    def __init__(self, transaction_coefficient, waiting_time_coefficient, pending_transaction_coefficient):
        super(BlockchainCustomEnv, self).__init__()

        # Define your custom observation space
        self.observation_space = spaces.Box(low=0, high=1, shape=(4,),
                                            dtype=np.float32)  # Example: Box space with 4 dimensions

        # Define your custom action space
        # 0 =  Wait for more transactions
        # 1 =  Create block with current transactions
        self.action_space = spaces.Discrete(2)  # Example: discrete action space with 2 possible actions

        self.blockchain = Blockchain()

        # Define the coefficients for the reward components
        self.transaction_coefficient = transaction_coefficient
        self.waiting_time_coefficient = waiting_time_coefficient
        self.pending_transaction_coefficient = pending_transaction_coefficient

    def step(self, action):
        # Perform one step in the environment given the selected action
        # Update the state, calculate the reward, and determine if the episode is done

        # Create transaction with random size
        global current_block_size
        transaction_size = random.randint(1, 100)
        transaction_data = "Transaction " + str(random.randint(1, 100) + 1)

        # Build transaction
        transaction = Transaction(time.time_ns(), transaction_data, transaction_size)
        number_of_transactions_included_in_block = 0

        # Calculate waiting time
        all_pending_transactions = self.blockchain.get_all_pending_transactions()
        waiting_time = 0
        for pending_transaction in all_pending_transactions:
            waiting_time += (time.time_ns() - pending_transaction.timestamp)

        # Calculate average waiting time
        if len(all_pending_transactions) > 0:
            waiting_time /= len(all_pending_transactions)
        else:
            waiting_time = 0

        pending_transactions_reward = 0

        manual_reward = 0

        # Work based on action
        if action == 0:
            # Wait for more transactions
            pending_transactions, current_block_size = self.blockchain.add_transaction(transaction, should_mine=False)
            pending_transactions_reward = pending_transactions

            # pending_transactions between 0 and 10
            manual_reward = pending_transactions * 0.9 - - (waiting_time/100000) * 0.15
            print("xxxxxxxxx: ", pending_transactions)
        elif action == 1:
            # Create block with current transactions
            len_of_transactions_included_in_block, current_block_size = self.blockchain.add_transaction(transaction,
                                                                                                        should_mine=True)
            print("BLOCK  ======================== ", len_of_transactions_included_in_block)
            number_of_transactions_included_in_block = len_of_transactions_included_in_block
            manual_reward = len_of_transactions_included_in_block * 0.7 - (waiting_time/100000) * 0.2
            if len_of_transactions_included_in_block < 50:
                manual_reward -= 100

        # reward = (
        #         self.transaction_coefficient * number_of_transactions_included_in_block +
        #         self.waiting_time_coefficient * waiting_time
        # )
        reward = manual_reward
        print("Reward: ", reward)

        observation = self._next_observation()

        done = False  # Example: episode is never done

        return observation, reward, done, {}

    def _next_observation(self):
        # Return the next observation to the agent
        block_size_of_previous_block = self.blockchain.get_latest_block().block_size
        average_waiting_time_of_last_block = self.blockchain.get_latest_block().average_waiting_time
        pending_transactions_count = len(self.blockchain.get_all_pending_transactions())
        mempool_growth = self.blockchain.current_block_size

        frame = normalize_array(np.array([
            block_size_of_previous_block,
            average_waiting_time_of_last_block,
            pending_transactions_count,
            mempool_growth
        ]))
        return frame

    def reset(self):
        # Reset the environment to its initial state and return the initial observation
        self.blockchain = Blockchain()
        return self._next_observation()

    def render(self, mode='human'):
        # Render the environment, e.g., print the current state or visualize it in a GUI
        # print(self.blockchain)

        # print()
        pass