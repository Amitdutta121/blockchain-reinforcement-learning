import gym
from gym import spaces
import hashlib
import datetime
import random
import time
import numpy as np
import pandas as pd
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
            print("Block created with size:---------------------------- ", self.current_block_size, " ----- ",
                  len_of_transactions)
            self.mine_block()
        else:
            waiting_time = (time.time_ns() - transaction.timestamp)
            self.waiting_times.append(waiting_time)
        return len_of_transactions, self.current_block_size

    def get_all_pending_transactions(self):
        return self.pending_transactions

    def get_all_pending_transactions_block_size_sum(self):
        return self.current_block_size

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
        print("Block info: ", new_block_size, " ----- ", new_block_size, " ----- ", average_waiting_time, " ----- ",
              len(data))
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


blockchain = Blockchain()

df = pd.read_csv('sample_transactions.csv')

main_waiting_time = []

for index, row in df.iterrows():
    print(row['transaction_size'], row['transaction_data'])
    transaction = Transaction(time.time_ns(), row['transaction_data'], row['transaction_size'])

    all_pending_transactions = blockchain.get_all_pending_transactions()
    waiting_time = 0
    for pending_transaction in all_pending_transactions:
        waiting_time += (time.time_ns() - pending_transaction.timestamp)

    # Calculate average waiting time
    if len(all_pending_transactions) > 0:
        waiting_time /= len(all_pending_transactions)
    else:
        waiting_time = 0

    if blockchain.get_all_pending_transactions_block_size_sum() > 2048:
        blockchain.add_transaction(transaction, should_mine=True)
    else:
        blockchain.add_transaction(transaction, should_mine=False)
        main_waiting_time.append(waiting_time)


print("Average waiting time: ", np.sum(main_waiting_time))
