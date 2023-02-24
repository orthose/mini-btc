from mini_btc import Miner, Wallet
from time import sleep


# Chargement des porte-feuilles
alice = Wallet("./wallets/alice.bin", "localhost", 8003, "localhost", 8000, verbose=1)
# La récompense de minage ira à Alice
# Donc à chaque bloc miné elle gagne forcément 50 BTC
alice_pubkey = alice.pubkey

bob = Wallet("./wallets/bob.bin", "localhost", 8004, "localhost", 8001, verbose=1)
bob_pubkey = bob.pubkey

# Le premier noeud n'est connecté à aucun autre
n1 = Miner(alice_pubkey, "localhost", 8000, difficulty=4, verbose=1)
# Le deuxième noeud est connecté au premier
n2 = Miner(alice_pubkey, "localhost", 8001, remote_host="localhost", remote_port=8000, difficulty=4, verbose=1)
# Le troisième noeud est aussi connecté au premier
n3 = Miner(alice_pubkey, "localhost", 8002, remote_host="localhost", remote_port=8000, difficulty=4, verbose=1)

# Démarrage des noeuds
n1.start(); sleep(1)
n2.start(); sleep(1)
n3.start(); sleep(1)

# Démarrage des porte-feuilles
alice.start(); sleep(1)
bob.start(); sleep(1)

# Génération du bloc de départ
# Pour lancer le minage on envoie des transactions vides
t1 = alice.empty_transfer(); sleep(1)
t2 = alice.empty_transfer(); sleep(10)

# Vérification du solde de Alice et Bob
alice.update_balance(); sleep(1)
assert 50 == alice.get_balance()

bob.update_balance(); sleep(1)
assert 0 == bob.get_balance()

# Vérification des transactions de Alice
alice.sync_block(); alice.get_proof(t1); alice.get_proof(t2); sleep(1)
assert alice.verify_proof(t1)
assert alice.verify_proof(t2)

# Alice envoie 10 BTC à Bob
t3 = alice.transfer(bob_pubkey, 10); sleep(1)
t4 = alice.empty_transfer(); sleep(10)

# Vérification du solde de Alice et Bob
alice.update_balance(); sleep(1)
assert (50-10) + 50 == alice.get_balance()

bob.update_balance(); sleep(1)
assert 10 == bob.get_balance()

# Vérification des transactions de Alice
alice.sync_block(); alice.get_proof(t3); alice.get_proof(t4); sleep(1)
assert alice.verify_proof(t3)
assert alice.verify_proof(t4)

# Alice envoie 5 BTC à Bob
t5 = alice.transfer(bob_pubkey, 5); sleep(1)
# Bob envoie 3 BTC à Alice
t6 = bob.transfer(alice_pubkey, 3)
sleep(10)

# Vérification du solde de Alice et Bob
alice.update_balance(); sleep(1)
assert (50-10) + (50-5) + (50+3) == alice.get_balance()

bob.update_balance(); sleep(1)
assert 10-3+5 == bob.get_balance()

# Vérification des transactions de Alice et Bob
alice.sync_block(); alice.get_proof(t5); sleep(1)
assert alice.verify_proof(t5)

# Note: Alice pourrait vérifier la transaction de Bob
bob.sync_block(); bob.get_proof(t6); sleep(1)
assert bob.verify_proof(t6)
