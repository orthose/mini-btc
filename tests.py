from Node import Node
from time import sleep


# Le premier noeud n'est connecté à aucun autre
n1 = Node("localhost", 8000)
# Le deuxième noeud est connecté au premier
n2 = Node("localhost", 8001, remote_host="localhost", remote_port=8000)
# Le troisième noeud est aussi connexté au premier
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

# Diffusion d'une requête sur le réseau
req = {"request": "TRANSACT", "from": "Alice", "to": "Bob", "amount": "1"}
n1.broadcast(req)

# Déconnexion du premier noeud
#del n1
n1.shutdown()
del n1
sleep(1)

# Diffusion d'une requête sur le réseau
req["from"] = "Bob"
req["to"] = "Alice"
req["amount"] = 2
n2.broadcast(req)
sleep(1)

n2.logging(n2.nodes)
n3.logging(n3.nodes)
