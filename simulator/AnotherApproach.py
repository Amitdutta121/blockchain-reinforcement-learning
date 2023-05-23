import hashlib
import time

class Block:
    def __init__(self, index, previous_hash, timestamp, data, hash):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.hash = hash

class Blockchain:
    def __init__(self, min_block_size):
        self.chain = []
        self.create_genesis_block()
        self.min_block_size = min_block_size
        self.current_block_size = 0
        self.pending_transactions = []

    def create_genesis_block(self):
        genesis_block = Block(0, "", time.time(), "Genesis Block", self.hash_block(""))
        self.chain.append(genesis_block)

    def add_block(self, data):
        self.pending_transactions.append(data)
        self.current_block_size += 1

        if self.current_block_size >= self.min_block_size:
            self.mine_block()

    def mine_block(self):
        index = len(self.chain)
        previous_hash = self.chain[-1].hash
        timestamp = time.time()
        block_data = "".join(self.pending_transactions)
        hash = self.hash_block(str(index) + previous_hash + str(timestamp) + block_data)
        new_block = Block(index, previous_hash, timestamp, block_data, hash)
        self.chain.append(new_block)

        self.pending_transactions = []
        self.current_block_size = 0

    def hash_block(self, data):
        sha = hashlib.sha256()
        sha.update(data.encode("utf-8"))
        return sha.hexdigest()

    def print_blockchain(self):
        for block in self.chain:
            print(f"Index: {block.index}")
            print(f"Previous Hash: {block.previous_hash}")
            print(f"Timestamp: {block.timestamp}")
            print(f"Data: {block.data}")
            print(f"Hash: {block.hash}")
            print()

# Example usage
blockchain = Blockchain(min_block_size=3)
blockchain.add_block("Transaction 1")
blockchain.add_block("Transaction 2")
blockchain.add_block("Transaction 3")

# The minimum block size is not met yet, so the block is not created
blockchain.print_blockchain()

blockchain.add_block("Transaction 4")
blockchain.print_blockchain()
