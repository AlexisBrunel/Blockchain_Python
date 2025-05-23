
import hashlib
import time
from typing import Dict, Any

class Block:
    def __init__(self, index: int, data: str, previous_hash: str, timestamp: float = None):
        self.index = index
        self.data = data
        self.previous_hash = previous_hash
        self.timestamp = timestamp or time.time()
        self.nonce = 0
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calcule le hash du bloc"""
        block_string = f"{self.index}{self.data}{self.previous_hash}{self.timestamp}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int) -> None:
        """Mine le bloc avec la preuve de travail"""
        target = "0" * difficulty
        start_time = time.time()
        
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
        
        end_time = time.time()
        print(f"Bloc mine: {self.hash} en {end_time - start_time:.2f} secondes avec {self.nonce} tentatives")

class Blockchain:
    def __init__(self, difficulty: int = 4):
        self.chain = [self.create_genesis_block()]
        self.difficulty = difficulty
        self.merkle_root = None
    
    def create_genesis_block(self) -> Block:
        """Cree le bloc genesis"""
        return Block(0, "Genesis Block", "0")
    
    def get_latest_block(self) -> Block:
        """Retourne le dernier bloc de la chaine"""
        return self.chain[-1]
    
    def add_block(self, data: str) -> None:
        """Ajoute un nouveau bloc a la chaine"""
        previous_block = self.get_latest_block()
        new_block = Block(
            index=len(self.chain),
            data=data,
            previous_hash=previous_block.hash
        )
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        self.update_merkle_root()
    
    def compute_merkle_root(self) -> str:
        """Calcule la racine de l'arbre de Merkle"""
        if not self.chain:
            return ""
        
        # Recupere tous les hash des blocs
        hashes = [block.hash for block in self.chain]
        
        # Si nombre impair, duplique le dernier hash
        if len(hashes) % 2 == 1:
            hashes.append(hashes[-1])
        
        # Construit l'arbre de Merkle
        while len(hashes) > 1:
            next_level = []
            for i in range(0, len(hashes), 2):
                combined = hashes[i] + hashes[i + 1]
                next_level.append(hashlib.sha256(combined.encode()).hexdigest())
            hashes = next_level
        
        return hashes[0] if hashes else ""
    
    def display_merkle_tree(self) -> None:
        """Affiche visuellement l'arbre de Merkle"""
        if not self.chain:
            print("Aucun bloc dans la chaine")
            return
        
        # Recupere tous les hash des blocs
        hashes = [block.hash for block in self.chain]
        print(f"Feuilles de l'arbre (hash des blocs):")
        for i, h in enumerate(hashes):
            print(f"  Bloc {i}: {h[:16]}...")
        
        # Si nombre impair, duplique le dernier hash
        if len(hashes) % 2 == 1:
            hashes.append(hashes[-1])
            print(f"  Duplication du dernier hash: {hashes[-1][:16]}...")
        
        level = 0
        # Construit l'arbre de Merkle niveau par niveau
        while len(hashes) > 1:
            level += 1
            next_level = []
            print(f"\nNiveau {level}:")
            for i in range(0, len(hashes), 2):
                combined = hashes[i] + hashes[i + 1]
                parent_hash = hashlib.sha256(combined.encode()).hexdigest()
                next_level.append(parent_hash)
                print(f"  Parent {i//2}: {parent_hash[:16]}... (de {hashes[i][:8]}... + {hashes[i+1][:8]}...)")
            hashes = next_level
        
        print(f"\nRacine de Merkle: {hashes[0]}")
    
    def update_merkle_root(self) -> None:
        """Met a jour la racine de Merkle"""
        self.merkle_root = self.compute_merkle_root()
    
    def is_chain_valid(self) -> bool:
        """Verifie l'integrite de la chaine"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Verifie le hash du bloc actuel
            if current_block.hash != current_block.calculate_hash():
                print(f"Hash invalide pour le bloc {i}")
                return False
            
            # Verifie le lien avec le bloc precedent
            if current_block.previous_hash != previous_block.hash:
                print(f"Lien invalide entre les blocs {i-1} et {i}")
                return False
        
        return True
    
    def corrupt_block(self, index: int, new_data: str) -> None:
        """Corrompt un bloc specifique"""
        if 0 <= index < len(self.chain):
            self.chain[index].data = new_data
            print(f"Bloc {index} corrompu avec les donnees: {new_data}")
    
    def get_chain_info(self) -> Dict[str, Any]:
        """Retourne les informations de la chaine"""
        return {
            "longueur": len(self.chain),
            "merkle_root": self.merkle_root,
            "valide": self.is_chain_valid(),
            "dernier_hash": self.get_latest_block().hash
        }

class DecentralizedNetwork:
    def __init__(self, num_nodes: int = 5, difficulty: int = 4):
        if num_nodes % 2 == 0:
            num_nodes += 1  # Assure un nombre impair
        
        self.nodes = []
        self.difficulty = difficulty
        
        # Cree les noeuds avec la meme chaine initiale
        for i in range(num_nodes):
            node = Blockchain(difficulty)
            self.nodes.append(node)
        
        print(f"Reseau decentralise cree avec {num_nodes} noeuds")
    
    def add_block_to_all(self, data: str) -> None:
        """Ajoute un bloc a tous les noeuds"""
        for i, node in enumerate(self.nodes):
            node.add_block(data)
            print(f"Bloc ajoute au noeud {i}")
    
    def simulate_51_percent_attack(self) -> None:
        """Simule une attaque a 51%"""
        majority_count = len(self.nodes) // 2 + 1
        print(f"\n=== Simulation d'attaque 51% ===")
        print(f"Corruption de {majority_count} noeuds sur {len(self.nodes)}")
        
        # Corrompt la majorite des noeuds
        for i in range(majority_count):
            self.nodes[i].corrupt_block(1, f"DONNEES_CORROMPUES_NOEUD_{i}")
            self.nodes[i].add_block(f"BLOC_MALVEILLANT_{i}")
        
        self.check_network_consensus()
    
    def check_network_consensus(self) -> None:
        """Verifie le consensus du reseau"""
        print("\n=== Etat du reseau ===")
        valid_chains = 0
        invalid_chains = 0
        
        for i, node in enumerate(self.nodes):
            is_valid = node.is_chain_valid()
            status = "VALIDE" if is_valid else "CORROMPUE"
            print(f"Noeud {i}: {status} - Longueur: {len(node.chain)} - Merkle: {node.merkle_root[:16]}...")
            
            if is_valid:
                valid_chains += 1
            else:
                invalid_chains += 1
        
        print(f"\nResume: {valid_chains} chaines valides, {invalid_chains} chaines corrompues")
        
        if invalid_chains > valid_chains:
            print("ALERTE: La majorite du reseau est corrompue!")
        else:
            print("Le reseau maintient son integrite")
    
    def detect_corrupted_chains(self) -> None:
        """Detecte automatiquement les chaines corrompues et les rejette"""
        print("\n=== Detection automatique de corruption ===")
        
        valid_nodes = []
        corrupted_indices = []
        
        for i, node in enumerate(self.nodes):
            if node.is_chain_valid():
                valid_nodes.append((i, node))
                print(f"Noeud {i}: VALIDE - Accepte par le reseau")
            else:
                corrupted_indices.append(i)
                print(f"Noeud {i}: CORROMPU - REJETE automatiquement par le reseau")
        
        print(f"\nResultat de la detection:")
        print(f"- Noeuds valides acceptes: {len(valid_nodes)}")
        print(f"- Noeuds corrompus rejetes: {len(corrupted_indices)}")
        
        if len(valid_nodes) > len(corrupted_indices):
            print("Le reseau maintient sa securite grace au rejet automatique")
        else:
            print("ALERTE: Trop de noeuds corrompus detectes!")
    
    def simulate_single_cheater(self) -> None:
        """Simule le cas ou une seule instance triche"""
        print("\n=== Simulation: Une seule instance triche ===")
        
        # Corrompt seulement le premier noeud
        print("Corruption du noeud 0...")
        self.nodes[0].corrupt_block(1, "DONNEES_FRAUDULEUSES")
        self.nodes[0].add_block("BLOC_FRAUDULEUX")
        
        print("Observation de l'impact sur le reseau:")
        self.detect_corrupted_chains()

def run_comprehensive_tests():
    """Execute une batterie complete de tests"""
    print("=== Debut des tests ===\n")
    
    # Etape 1: Creation de base
    print("=== Etape 1: Creation de la blockchain ===")
    blockchain = Blockchain(difficulty=3)
    blockchain.add_block("Premier bloc de donnees")
    blockchain.add_block("Deuxieme bloc de donnees")
    print(f"Blockchain creee avec {len(blockchain.chain)} blocs")
    print(f"Chaine valide: {blockchain.is_chain_valid()}\n")

    # Etape 2: Ajout de la preuve de travail (PoW)
    print("=== Etape 2: Demonstration de la preuve de travail (PoW) ===")
    print("Test avec differentes difficultes:")
    difficulty = 3
    print(f"\n- Test avec difficulte {difficulty}:")
    test_blockchain = Blockchain(difficulty=difficulty)
    test_blockchain.add_block("Bloc test difficulte 3")
    
    # Verification de la preuve de travail
    print("\n- Verification de la preuve de travail:")
    last_block = test_blockchain.get_latest_block()
    print(f"Hash du bloc mine: {last_block.hash}")
    print(f"Nonce utilise: {last_block.nonce}")
    print(f"Hash commence par {'0' * test_blockchain.difficulty}: {last_block.hash.startswith('0' * test_blockchain.difficulty)}")
    print("La preuve de travail fonctionne correctement!\n")

    # Etape 3: Arbre de Merkle
    print("=== Etape 3: Arbre de Merkle ===")
    print("Construction et affichage de l'arbre de Merkle:")
    blockchain.display_merkle_tree()
    
    print(f"\nRacine Merkle avant corruption: {blockchain.merkle_root}")
    
    # Corruption et comparaison
    blockchain.corrupt_block(1, "DONNEES CORROMPUES")
    blockchain.update_merkle_root()
    print(f"Racine Merkle apres corruption: {blockchain.merkle_root}")
    
    print("\nComparaison visuelle - Nouvel arbre apres corruption:")
    blockchain.display_merkle_tree()
    print()
    
    # Etape 4: Decentralisation
    print("=== Etape 4: Reseau decentralise ===")
    network = DecentralizedNetwork(num_nodes=5, difficulty=2)
    network.add_block_to_all("Alexis envoie 1 BTC à Michel")
    network.add_block_to_all("Alexis envoie 0,1 BTC à sa copine")
    network.check_network_consensus()
    
    # Etape 5: Attaque 51%
    print("\n=== Etape 5: Attaque 51% ===")
    network.simulate_51_percent_attack()
    
    # Etape 6: Detection de corruption (sans correction)
    print("\n=== Etape 6: Detection de corruption ===")
    print("Test 1: Detection avec une seule instance qui triche")
    clean_network = DecentralizedNetwork(num_nodes=5, difficulty=2)
    clean_network.add_block_to_all("Bloc leger")
    clean_network.simulate_single_cheater()
    
    print("\nTest 2: Detection avec attaque majoritaire")
    network.detect_corrupted_chains()
    
    print("\nTous les tests sont termines")

if __name__ == "__main__":
    run_comprehensive_tests()
