from mini_btc import FullNode, Wallet
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

w = Wallet("wallet.bin", "localhost", 8003, "localhost", 8000)
w.start()

# Demande de transaction
w.transfer("abcdefgh", 1)
sleep(1)

# Vérification de l'état des noeuds
w.logging(w.nodes)
n1.logging(n1.nodes)
n2.logging(n2.nodes)
n3.logging(n3.nodes)
n1.logging(n1.buf_trans)
n2.logging(n2.buf_trans)
n3.logging(n3.buf_trans)
