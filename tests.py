from Node import Node


# Le premier noeud n'est connecté à aucun autre
n1 = Node("localhost", 8000)
# Le deuxième noeud est connecté au premier
n2 = Node("localhost", 8001, remote_host="localhost", remote_port=8000)
# Le troisième noeud est aussi connexté au premier
n3 = Node("localhost", 8002, remote_host="localhost", remote_port=8000)

n1.start()
n2.start()
n3.start()
