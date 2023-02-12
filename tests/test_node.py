from mini_btc import Node
from time import sleep


# Le premier noeud n'est connecté à aucun autre
n1 = Node("localhost", 8000)
# Le deuxième noeud est connecté au premier
n2 = Node("localhost", 8001, remote_host="localhost", remote_port=8000)
# Le troisième noeud est aussi connecté au premier
n3 = Node("localhost", 8002, remote_host="localhost", remote_port=8000)

# Démarrage des noeuds
n1.start()
n2.start()
sleep(1)
n3.start()
sleep(1)

# Vérification des voisins
n1.logging(n1.nodes)
n2.logging(n2.nodes)
n3.logging(n3.nodes)

# Diffusion d'une transaction vide sur le réseau
req = {'request': 'TRANSACT', 'tx': {'locktime': 1676235668.405151, 'input': [], 'output': [], 'hash': '4b22550a32452d9b6d7e7f82d2a2015c0083b289e1fadb538c9f868b0e6d9b4e'}}
n1.broadcast(req)
sleep(1)

# Déconnexion du premier noeud
n1.shutdown()
del n1
sleep(1)

# Diffusion d'une requête sur le réseau
req = {'request': 'TRANSACT', 'tx': {'locktime': 1676235617.8596997, 'input': [], 'output': [], 'hash': '1c060157e9af77b5dcf6d75efbfde7237fc05c9b423afada0ce2e7280790e964'}}
n2.broadcast(req)
sleep(1)

n2.logging(n2.nodes)
n3.logging(n3.nodes)

# Envoi d'un paquet privé de n2 vers n3
req = {"request": "GET_BLOCKS"}
n2.send("localhost", 8002, req)
