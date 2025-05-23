import hashlib
import time
import random
import copy

class Block:
    def __init__(self, index, data, previous_hash, difficulty=4):
        self.index = index
        self.timestamp = time.time()
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.difficulty = difficulty
        self.hash = self.mine_block()

    def calculate_hash(self):
        content = f"{self.index}{self.timestamp}{self.data}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(content.encode()).hexdigest()

    def mine_block(self):
        prefix = "0" * self.difficulty
        while True:
            hash_val = self.calculate_hash()
            if hash_val.startswith(prefix):
                return hash_val
            self.nonce += 1

class MerkleTree:
    @staticmethod
    def calculate_merkle_root(hashes):
        if not hashes:
            return None
        current_level = hashes[:]
        while len(current_level) > 1:
            if len(current_level) % 2 != 0:
                current_level.append(current_level[-1])
            next_level = []
            for i in range(0, len(current_level), 2):
                combined = current_level[i] + current_level[i+1]
                next_level.append(hashlib.sha256(combined.encode()).hexdigest())
            current_level = next_level
        return current_level[0]

class Blockchain:
    def __init__(self, difficulty=4):
        self.difficulty = difficulty
        self.chain = [self.create_genesis_block()]
        self.merkle_root = None

    def create_genesis_block(self):
        return Block(0, "Genesis Block", "0", self.difficulty)

    def add_block(self, data):
        prev_hash = self.chain[-1].hash
        new_block = Block(len(self.chain), data, prev_hash, self.difficulty)
        self.chain.append(new_block)

    def compute_merkle_root(self):
        hashes = [b.hash for b in self.chain]
        self.merkle_root = MerkleTree.calculate_merkle_root(hashes)
        return self.merkle_root

    def is_chain_valid(self):
        prefix = "0" * self.difficulty
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            prev = self.chain[i-1]
            # Check hash correctness
            if current.hash != current.calculate_hash():
                print(f"Bloc #{current.index} hash invalide !")
                return False
            # Check chain link
            if current.previous_hash != prev.hash:
                print(f"Bloc #{current.index} lien au bloc précédent invalide !")
                return False
            # Check PoW difficulty
            if not current.hash.startswith(prefix):
                print(f"Bloc #{current.index} difficulté PoW non respectée !")
                return False
        # Check Merkle root consistency
        recalculated = MerkleTree.calculate_merkle_root([b.hash for b in self.chain])
        if recalculated != self.merkle_root:
            print("Racine Merkle invalide !")
            return False
        return True

    def display(self):
        print(f"Blockchain (longueur={len(self.chain)}, racine Merkle={self.merkle_root[:10]}...) :")
        for b in self.chain:
            print(f" Bloc #{b.index} | Hash: {b.hash[:10]}... | PrevHash: {b.previous_hash[:10]}... | Data: {b.data}")

class Network:
    def __init__(self, node_count, difficulty=4):
        assert node_count % 2 == 1, "Le nombre de noeuds doit être impair pour simuler l'attaque 51%"
        self.nodes = []
        self.difficulty = difficulty
        for i in range(node_count):
            bc = Blockchain(difficulty)
            # Ajout de blocs "Donnée #i" de 1 à 8 (8 blocs + genesis)
            for j in range(1, 9):
                bc.add_block(f"Donnée #{j}")
            bc.compute_merkle_root()
            self.nodes.append(bc)

    def display_all(self):
        for i, bc in enumerate(self.nodes):
            print(f"\n=== Noeud {i} ===")
            bc.display()

    def validate_all(self):
        print("\n--- Validation individuelle des chaînes ---")
        results = []
        for i, bc in enumerate(self.nodes):
            valid = bc.is_chain_valid()
            results.append(valid)
            print(f"Noeud {i} : {'✅ Valide' if valid else '❌ Corrompu'}")
        return results

    def majority_vote(self):
        # On compte le nombre de chaînes valides
        valides = sum(1 for bc in self.nodes if bc.is_chain_valid())
        if valides > len(self.nodes)//2:
            print(f"\n⚖️  Majorité (51%) valide ({valides} sur {len(self.nodes)})")
            return True
        else:
            print(f"\n⚠️  Majorité corrompue ({len(self.nodes)-valides} sur {len(self.nodes)})")
            return False

    def corrupt_nodes(self, indices, blocks_to_corrupt):
        # Corruption par changement de données dans blocs spécifiques
        for idx in indices:
            bc = self.nodes[idx]
            for bidx in blocks_to_corrupt:
                if 0 <= bidx < len(bc.chain):
                    bc.chain[bidx].data = "FALSIFIED DATA"
                    # recalcul du hash sans minage pour simuler falsification (hash incorrect)
                    bc.chain[bidx].hash = bc.chain[bidx].calculate_hash()
            # recalculer racine Merkle
            bc.compute_merkle_root()

    def run_attack_51(self):
        # On corrompt la majorité +1 noeud
        half = len(self.nodes)//2
        to_corrupt = list(range(half + 1))
        print(f"\n--- Attaque 51% : Corruption des noeuds {to_corrupt} ---")
        # Exemple: corrompre tous les blocs sauf genesis (bloc 0)
        for idx in to_corrupt:
            self.corrupt_nodes([idx], list(range(1,9)))

def tests():
    # Initialisation réseau 5 noeuds (impair)
    net = Network(node_count=5, difficulty=5)
    print("\nInitialisation réseau avec 5 noeuds, tous valides :")
    net.display_all()

    # Test validité initiale (toutes valides)
    print("\nValidation initiale des chaînes :")
    assert all(net.validate_all())

    # Corruption mineure dans un seul noeud
    print("\n--- Corruption mineure dans le noeud 0 (bloc 3) ---")
    net.corrupt_nodes([0], [3])
    net.display_all()
    results = net.validate_all()
    print(f"Majority vote (doit être valide): {net.majority_vote()}")
    assert not results[0]
    assert results[1]
    assert results[2]
    assert results[3]
    assert results[4]

    # Attaque 51%
    net.run_attack_51()
    net.display_all()
    results = net.validate_all()
    majority = net.majority_vote()
    assert not majority  # majorité corrompue

    # Correction : reconstruire les noeuds corrompus en bons
    print("\n--- Correction des noeuds corrompus ---")
    for idx in range(len(net.nodes)):
        net.nodes[idx] = copy.deepcopy(Network.node_template(net.difficulty))
    net.display_all()

    # Validité après correction
    results = net.validate_all()
    assert all(results)
    print("\nTous les noeuds sont à nouveau valides.")

if __name__ == "__main__":
    # Exécution des tests
    tests()
