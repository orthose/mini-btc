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
genesis = {'index': 0, 'hash': None, 'root': '3e85455d74d714c9c9fad556cd3b6f0d1a91f54338c2fe43ee9dff0861fa6c70', 'nonce': 759273861, 'tx': [
    {'locktime': 1677271598.235741, 'input': [], 'output': [], 'hash': '21419e2a06f05a966bd73b3660b0faffa9397be6671cfa5a506f457e40779c47'},
    {'locktime': 1677271600.9368517, 'input': [], 'output': [], 'hash': 'c151bf642b1a9e63acf3860cbaaa239823935c6d07757cd2d97a0e0e723ea0d6'},
    {'locktime': 1677271600.9819515, 'input': [], 'output': [
        {'address': '668wc7STftWcCMUR8o9G62epry1GCDc5PiMnWmXySzW8', 'value': 50, 'lock': 'BQfcHxQKFtLLEA9o2azM9N2owM1eaArtwEPJYtguXQPyUohbFubHLjBsb3zQuQSgCEnJ5ZL87yKZ2mZomnKasa7HGgGHG7Rabzo9PjaAt4R6h8RyWRUtSHQCAArqqXagy7rTpfDi4BKoSXcpWsNgfnjBttcd3rbdBxrL9pGHZvPP7vsA2cPPYW1k2LNezr2MW6NSWRmevXYYbq9Ly9WgKWUTXx6yhYTiuWZMG4P8xCNwDqXZPDwUWhcwV5Bf4w4V9kodG9yiJnxRax4bF4CzveJoR68ehYaF1ePNMcnA8cR1SPFTpMJLnQXNv35hGwbz2PRQ4yFPfrYiwLEk1yoaYKWisZj9QyKCnqxRxrGW36TtuBLhksQoBnEkddginsDYezxFG7WZtbwuQWBQzohmTBWd51f9BK3koHrZpUPXrvhgJchmKcqdbH2YRoyMRNSAkADyLBoPphdvbPNEBaHKoDjXNnLXe5ZBEWxeW3qdrXTsPRXmhLYbZ2HbKoAiAg1mWcSqSpZZLV89xJXP1p6Wb1TDAZm8BGLFs9iCLMPZcGzBZ2cPqszor7b8ZngEYDznvKBDbkebq927fWWKwMEcBnLu9KrZg CHECKSIG'}],
    'hash': 'fae3166e856571a85ca5ed144d3f45d768fd5b422d3205622fc5c75a5e9d61c3'}]}
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

assert 1 == len(n1.buf_tx)
assert 1 == len(n2.buf_tx)
assert 1 == len(n3.buf_tx)

# Demande de blocs à un noeud
n1.ledger = []
req = {"request": "GET_BLOCKS"}
n1.send("localhost", 8001, req)
sleep(1)

# Vérification de l'état de la blockchain sur chaque noeud
n1.logging(n1.ledger)
n2.logging(n2.ledger)
n3.logging(n3.ledger)
