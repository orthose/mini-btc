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
genesis =  {'index': 0, 'hash': None, 'nonce': 334155872, 'trans': [
    {'locktime': 1676235615.5138822, 'input': [], 'output': [], 'hash': '10b484a625322caadb9f1c6da2d30a0e140677febc9f9a648f46001a5e8fc756'},
    {'locktime': 1676235617.8596997, 'input': [], 'output': [], 'hash': '1c060157e9af77b5dcf6d75efbfde7237fc05c9b423afada0ce2e7280790e964'},
    {'locktime': 1676235617.9343636, 'input': [], 'output': [
        {'address': '668wc7STftWcCMUR8o9G62epry1GCDc5PiMnWmXySzW8', 'value': 50, 'lock': 'BQfcHxQKFtLLEA9o2azM9N2owM1eaArtwEPJYtguXQPyUohbFubHLjBsb3zQuQSgCEnJ5ZL87yKZ2mZomnKasa7HGgGHG7Rabzo9PjaAt4R6h8RyWRUtSHQCAArqqXagy7rTpfDi4BKoSXcpWsNgfnjBttcd3rbdBxrL9pGHZvPP7vsA2cPPYW1k2LNezr2MW6NSWRmevXYYbq9Ly9WgKWUTXx6yhYTiuWZMG4P8xCNwDqXZPDwUWhcwV5Bf4w4V9kodG9yiJnxRax4bF4CzveJoR68ehYaF1ePNMcnA8cR1SPFTpMJLnQXNv35hGwbz2PRQ4yFPfrYiwLEk1yoaYKWisZj9QyKCnqxRxrGW36TtuBLhksQoBnEkddginsDYezxFG7WZtbwuQWBQzohmTBWd51f9BK3koHrZpUPXrvhgJchmKcqdbH2YRoyMRNSAkADyLBoPphdvbPNEBaHKoDjXNnLXe5ZBEWxeW3qdrXTsPRXmhLYbZ2HbKoAiAg1mWcSqSpZZLV89xJXP1p6Wb1TDAZm8BGLFs9iCLMPZcGzBZ2cPqszor7b8ZngEYDznvKBDbkebq927fWWKwMEcBnLu9KrZg CHECKSIG'}], 'hash': '8c5c5dbf814d798e852f0199112706f38b438c9cf29a795cdcd50907d4bd9d9f'}]}
n1.ledger.append(genesis)

# Soumission de ce premier bloc sur le réseau
req = {"request": "SUBMIT_BLOCK", "host": "localhost", "port": 8000, "block": genesis}
n1.broadcast(req)
sleep(1)

# Vérification de l'état de la blockchain sur chaque noeud
n1.logging(n1.ledger)
n2.logging(n2.ledger)
n3.logging(n3.ledger)

# Diffusion d'une transaction vide sur le réseau
req = {'request': 'TRANSACT', 'tx': {'locktime': 1676235668.405151, 'input': [], 'output': [], 'hash': '4b22550a32452d9b6d7e7f82d2a2015c0083b289e1fadb538c9f868b0e6d9b4e'}}
n1.broadcast(req)
sleep(1)

n1.logging(n1.buf_trans)
n2.logging(n2.buf_trans)
n3.logging(n3.buf_trans)

# Demande de blocs à un noeud
n1.ledger = []
req = {"request": "GET_BLOCKS"}
n1.send("localhost", 8001, req)
sleep(1)

# Vérification de l'état de la blockchain sur chaque noeud
n1.logging(n1.ledger)
n2.logging(n2.ledger)
n3.logging(n3.ledger)
