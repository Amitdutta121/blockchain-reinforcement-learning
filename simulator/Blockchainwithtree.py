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
    def __init__(self, timestamp, data, previous_hash, block_size, average_waiting_time):
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.block_size = block_size
        self.merkle_root = self.calculate_merkle_root()
        self.hash = self.calculate_hash()
        self.average_waiting_time = average_waiting_time

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
        self.min_block_size = 1024  # 1 MB = 1000 KB
        self.pending_transactions = []
        self.current_block_size = 0
        self.waiting_times = []

    def create_genesis_block(self):
        transaction = Transaction(time.time_ns(), "Genesis Block", 1)
        return Block(time.time_ns(), [transaction], "0", 1, 0)

    def get_latest_block(self):
        return self.chain[-1]

    def add_transaction(self, transaction):
        self.pending_transactions.append(transaction)
        self.current_block_size += transaction.block_size

        if self.current_block_size >= self.min_block_size:
            self.mine_block()
        else:
            waiting_time = (time.time_ns() - transaction.timestamp)
            self.waiting_times.append(waiting_time)
        print("NO MINE: ", len(self.pending_transactions))

    def mine_block(self):
        data = self.pending_transactions[:self.min_block_size]

        waiting_time = 0
        average_waiting_time = 0


        for transaction in data:
            waiting_time += (time.time_ns() - transaction.timestamp)

        # Average waiting time
        if len(data) > 0:
            average_waiting_time = waiting_time / len(data)


        new_block = Block(time.time_ns(), data, self.get_latest_block().hash, self.min_block_size, average_waiting_time)
        self.add_block(new_block)
        self.pending_transactions = self.pending_transactions[self.min_block_size:]
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


# Create a blockchain
blockchain = Blockchain()

df = pd.read_csv('sample_transactions.csv')

for index, row in df.iterrows():
    print(row['transaction_size'], row['transaction_data'])
    transaction = Transaction(time.time_ns(), row['transaction_data'], row['transaction_size'])
    blockchain.add_transaction(transaction)
# Generate random transactions
# for i in range(100):
#     transaction_size = random.randint(1, 100)  # Random transaction size between 1 and 1000 KB
#     transaction_data = "Transaction " + str(i + 1)
#     transaction = Transaction(time.time_ns(), transaction_data, transaction_size)
#     blockchain.add_transaction(transaction)
#     time.sleep(random.uniform(0.1, 0.5))  # Random time delay between transactions

# Mine the final block if there are remaining transactions
if len(blockchain.pending_transactions) > 0:
    blockchain.mine_block()
avg_wait_time = 0
# Print the blocks in the blockchain
for block in blockchain.chain:
    print("Timestamp:", block.timestamp)
    print("Data:", [transaction.data for transaction in block.data])
    print("Merkle Root:", block.merkle_root)
    print("Hash:", block.hash)
    print("Previous Hash:", block.previous_hash)
    print("Block Size:", block.block_size)
    print()
    avg_wait_time += block.average_waiting_time


print("Average Waiting Time:", avg_wait_time/len(blockchain.chain), "ns")

# Validate the blockchain
print("Is blockchain valid?", blockchain.is_chain_valid())

print(blockchain.waiting_times)

# Calculate average waiting time
# if len(blockchain.waiting_times) > 0:
#     average_waiting_time = np.sum(blockchain.waiting_times)
#     print("Average Waiting Time:", average_waiting_time, "ns")
# else:
#     print("No waiting times recorded.")




