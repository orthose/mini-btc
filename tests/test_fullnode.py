from mini_btc import FullNode
from time import sleep


# Le premier noeud n'est connecté à aucun autre
n1 = FullNode("localhost", 8000)
# Le deuxième noeud est connecté au premier
n2 = FullNode("localhost", 8001, remote_host="localhost", remote_port=8000)
# Le troisième noeud est aussi connecté au premier
n3 = FullNode("localhost", 8002, remote_host="localhost", remote_port=8000)

# Démarrage des noeuds
n1.start()
n2.start()
sleep(1)
n3.start()
sleep(1)

# Création du premier bloc sur n1
genesis = {"index": 0, "hash": None, "nonce": 249, "trans": []}
n1.ledger.append(genesis)

# Soumission de ce premier bloc sur le réseau
req = {"request": "SUBMIT_BLOCK", "host": "localhost", "port": 8000, "block": genesis}
n1.broadcast(req)
sleep(1)

# Vérification de l'état de la blockchain sur chaque noeud
n1.logging(n1.ledger)
n2.logging(n2.ledger)
n3.logging(n3.ledger)

# Diffusion d'une requête sur le réseau
req = {"request": "TRANSACT", "from": "Alice", "to": "Bob", "amount": "1"}
n1.broadcast(req)
sleep(1)

n1.logging(n1.buf_trans)
n2.logging(n2.buf_trans)
n3.logging(n3.buf_trans)

# Demande de blocs à un noeud
n1.ledger = []
req = {"request": "GET_BLOCKS", "start": 0}
n1.send("localhost", 8001, req)
sleep(1)

# Vérification de l'état de la blockchain sur chaque noeud
n1.logging(n1.ledger)
n2.logging(n2.ledger)
n3.logging(n3.ledger)
