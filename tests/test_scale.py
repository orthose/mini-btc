from mini_btc import Miner, Wallet
from time import sleep
import random


# Création de 5 mineurs
port = 8000
miners = [Miner("localhost", port)]
for _ in range(5):
    port += 1
    miners.append(Miner("localhost", port, "localhost", 8000))

# Démarrage des mineurs
for m in miners:
    m.start()
    sleep(1)

for m in miners:
    m.logging(m.nodes)

# Création du bloc de départ
miners[0].genesis()

# Création d'un portefeuille
port += 1
wallet = Wallet("./wallet.bin", "localhost", port, "localhost", 8000)

def pseudo(size=16):
    alpha = [chr(i) for i in range(97, 123)]
    return ''.join(random.sample(alpha, size))

# Soumission de 21 transactions aléatoires
for _ in range(21):
    wallet.transfer(dest=pseudo(), amount=random.randint(1, 10))

# Le minage dure environ 3 minutes pour 21 / 3 = 7 blocs
sleep(3 * 60)
print("\n### RESULTATS ###\n")
for m in miners:
    m.logging([block["nonce"] for block in m.ledger])
