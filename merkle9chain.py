import hashlib
import time

class Block:
    def __init__(self, index, data, previous_hash, difficulty=5):
        self.index = index
        self.timestamp = time.time()
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.mine_block(difficulty)

    def calculate_hash(self):
        content = f"{self.index}{self.timestamp}{self.data}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(content.encode()).hexdigest()

    def mine_block(self, difficulty):
        prefix = "0" * difficulty
        while True:
            hash_attempt = self.calculate_hash()
            if hash_attempt.startswith(prefix):
                return hash_attempt
            self.nonce += 1

class MerkleTree:
    @staticmethod
    def calculate_merkle_root(hashes):
        if not hashes:
            return None
        while len(hashes) > 1:
            if len(hashes) % 2 != 0:
                hashes.append(hashes[-1])
            new_level = []
            for i in range(0, len(hashes), 2):
                combined = hashes[i] + hashes[i + 1]
                new_hash = hashlib.sha256(combined.encode()).hexdigest()
                new_level.append(new_hash)
            hashes = new_level
        return hashes[0]

class Blockchain:
    def __init__(self, difficulty=5):
        self.difficulty = difficulty
        self.chain = [self.create_genesis_block()]
        self.merkle_root = None

    def create_genesis_block(self):
        return Block(0, "Genesis Block", "0", self.difficulty)

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, data):
        previous_hash = self.get_latest_block().hash
        block = Block(len(self.chain), data, previous_hash, self.difficulty)
        self.chain.append(block)

    def compute_merkle_root(self):
        block_hashes = [block.hash for block in self.chain]
        self.merkle_root = MerkleTree.calculate_merkle_root(block_hashes)
        return self.merkle_root

    def is_chain_valid(self):
        prefix = "0" * self.difficulty
        invalid_blocks = []

        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.calculate_hash():
                invalid_blocks.append((i, "Hash falsifié"))
            if current.previous_hash != previous.hash:
                invalid_blocks.append((i, "previous_hash incorrect"))
            if not current.hash.startswith(prefix):
                invalid_blocks.append((i, "Difficulté non respectée"))

        recalculated_merkle = MerkleTree.calculate_merkle_root([b.hash for b in self.chain])
        if recalculated_merkle != self.merkle_root:
            print(" Merkle Root invalide")

        if invalid_blocks:
            print(f" {len(invalid_blocks)} problème(s) détecté(s) dans la chaîne:")
            for idx, raison in invalid_blocks:
                print(f"  - Bloc #{idx} : {raison}")
            return False
        else:
            print(" Blockchain et Merkle Root valides.")
            return True

    def display(self):
        for b in self.chain:
            print(f"Block #{b.index} | Hash: {b.hash[:10]}... | Data: {b.data}")

def falsify_block(blockchain, indices_to_falsify):
    for idx in indices_to_falsify:
        blockchain.chain[idx].data = "FALSIFIED DATA"
        blockchain.chain[idx].hash = blockchain.chain[idx].calculate_hash()

def run_verification(name, chain):
    print(f"\n🔍 Vérification de la {name}")
    valid = chain.is_chain_valid()
    print("État :", " Intègre" if valid else " Compromise")

if __name__ == "__main__":
    # Création des 9 blockchains
    blockchains = []
    for _ in range(9):
        bc = Blockchain(difficulty=5)
        for i in range(1, 9):
            bc.add_block(f"Donnée #{i}")
        bc.compute_merkle_root()
        blockchains.append(bc)

    # Affichage des 2 premières chaînes valides
    print("\n Chaîne 0 (intègre) :")
    blockchains[0].display()
    print("\n Chaîne 1 (intègre) :")
    blockchains[1].display()

    # Falsifications variées sur chaînes 2 à 8
    falsify_block(blockchains[2], [3])              # 1 bloc falsifié
    falsify_block(blockchains[3], [2, 4, 6])        # 3 blocs falsifiés
    falsify_block(blockchains[4], [1, 2, 3, 4])     # 4 blocs falsifiés (début)
    falsify_block(blockchains[5], [5, 6, 7, 8])     # 4 derniers blocs falsifiés
    falsify_block(blockchains[6], list(range(1, 9)))# Presque toute la chaîne falsifiée (sauf genesis)
    falsify_block(blockchains[7], [1, 3, 5, 7])     # blocs impairs falsifiés
    falsify_block(blockchains[8], [0,1,2,3,4,5,6,7,8]) # falsifie TOUT (même genesis)

    # Vérifications avec détails
    for i, bc in enumerate(blockchains):
        run_verification(f"chaîne {i}", bc)
