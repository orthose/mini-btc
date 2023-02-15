from mini_btc import Miner, Wallet
from time import sleep
import random


# Chargement du porte-feuille de Alice
alice = Wallet("./wallets/alice.bin", "localhost", 8000, "localhost", 8001, verbose=0)
# La récompense de minage de 50 BTC va à Alice
alice_pubkey = alice.pubkey

# Création de 5 mineurs
port = 8001
miners = [Miner(alice_pubkey, "localhost", port, difficulty=4, verbose=1)]
for _ in range(5):
    port += 1
    miners.append(Miner(alice_pubkey, "localhost", port, "localhost", 8001, difficulty=4, verbose=1))

# Démarrage des mineurs
for m in miners:
    m.start()
    sleep(1)

for m in miners:
    m.logging(m.nodes)

# Démarrage du porte-feuille
alice.start()

# Soumission de 32 transactions vides
for _ in range(32):
    alice.empty_transfer()

# Création d'un mineur se connectant en retard pour tester LIST_BLOCKS
# Il ne pourra pas miner parce qu'il n'a pas reçu les transactions
sleep(10)
port += 1
miners.append(Miner(alice_pubkey, "localhost", port, "localhost", 8001, difficulty=4, verbose=1))
miners[-1].start()

# Le minage dure environ 2 minutes pour 32 / 2 = 16 blocs
sleep(2 * 60)
print("\n### RESULTATS ###\n")
for m in miners:
    m.logging([block["nonce"] for block in m.ledger])

alice.update_balance(); sleep(1)
balance = alice.get_balance()
print(f"{balance} BTC")
assert 50 * 16 == balance
