from mini_btc import Miner, Wallet
from time import sleep


# Le premier noeud n'est connecté à aucun autre
n1 = Miner("localhost", 8000)
# Le deuxième noeud est connecté au premier
n2 = Miner("localhost", 8001, remote_host="localhost", remote_port=8000)
# Le troisième noeud est aussi connecté au premier
n3 = Miner("localhost", 8002, remote_host="localhost", remote_port=8000)

# Démarrage des noeuds
n1.start()
n2.start()
sleep(1)
n3.start()
sleep(1)

w = Wallet("./wallet.bin", "localhost", 8003, "localhost", 8000)
w.start()

# Génération du bloc de départ
n1.genesis()
sleep(1)

n1.logging(n1.ledger)
n2.logging(n2.ledger)
n3.logging(n3.ledger)

w.transfer(dest="ykvoezkvoek", amount=1)
w.transfer(dest="ejiajciajei", amount=2)
w.transfer(dest="ckkziizhrki", amount=3)
sleep(40)

n1.logging(n1.ledger)
n2.logging(n2.ledger)
n3.logging(n3.ledger)
