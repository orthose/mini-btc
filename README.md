# Introduction
Projet de création d'une blockchain bitcoin locale simplifiée
basée sur une architecture pair à pair construite manuellement.

# Architecture
La classe **Node** est la classe bas niveau du réseau pair à pair.
Elle est chargée d'acheminer les paquets sur le réseau au travers de 2 primitives.
* **BROADCAST**: Diffusion d'un paquet sur le réseau à tous les noeuds.
* **PRIVATE**: Transmission directe d'un paquet entre 2 noeuds du réseau.

La classe **FullNode** ajoute une couche encapsulée dans les paquets gérés par
la classe **Node**. Elle permet cette fois de traiter des requêtes sur la blockchain,
stocke le registre des blocs et le met à jour.
* **TRANSACT**: Transaction à ajouter au tampon des transactions pas encore ajoutées au registre.
* **SUBMIT_BLOCK**: Soumission d'un bloc à ajouter au registre.
* **GET_BLOCKS**: Demande privée de la copie du registre du noeud.
Permet la connexion dynamique de nouveaux noeuds sur le réseau.
* **LIST_BLOCKS**: Réponse privée suite à une demande GET_BLOCKS.
* **GET_BALANCE**: Demande privée d'un porte-feuille des UTXO concernant son adresse.

La classe **Miner** étend les fonctionnalités de la classe FullNode en ajoutant
la possibilité de miner des blocs. Le mineur est capable de démarrer dynamiquement
le minage lorsqu'il a reçu suffisamment de transactions dans son tampon
et de s'arrêter lorsqu'il n'y en a plus assez.
Il est nécessaire de donner une clé publique au mineur à laquelle sera attribuée
la récompense de minage sous forme d'une UTXO incluse directement dans le bloc miné.

La classe **Wallet** représente le porte-feuille. Il est connecté à un seul FullNode.
Il stocke le couple (clé privée, clé publique) de l'utilisateur.
Il lui permet d'envoyer des transactions et de consulter le solde associé à son adresse.
* **TRANSACT**: Envoi d'une transaction à diffuser sur le réseau.
* **GET_BALANCE**: Demande privée du solde associé à l'adresse du porte-feuille.
* **BALANCE**: Liste des UTXO envoyées par le noeud en réponse de GET_BALANCE.
![Architecture](./archi.jpg)

# Spécificités de l'implémentation
De nombreux choix de règles sont possibles pour implémenter une blockchain.
Globalement, j'ai essayé de réaliser une simulation réaliste mais pas optimisée
ni sécurisée.

* **Quel est l'algorithme de hachage utilisé pour le minage ?**
J'utilise l'algorithme **SHA256** comme Bitcoin.

* **Comment est créé un porte-feuille utilisateur ?**
J'utilise l'algorithme [DSA](https://pycryptodome.readthedocs.io/en/latest/src/signature/dsa.html)
pour générer le couple (clé privée, clé publique).
C'est un algorithme adapté pour la signature numérique.
L'adresse est simplement la hash SHA256 de la clé publique.

* **Comment le solde de l'utilisateur est-il tenu à jour ?**
J'ai implémenté le système de transactions UTXO (Unspent Transaction Output)
utilisé dans Bitcoin. Un porte-feuille détient une liste de transactions
qui lui adressent de l'argent. Il peut ensuite consommer ces transactions
pour envoyer de l'argent à d'autres adresses.

* **Comment les transactions sont-elles validées ?**
Les transactions sont validées par les mineurs. Si elles sont valides elles sont
ajoutées à un bloc. Dans Bitcoin, une transaction UTXO est verrouillée par un
programme **lock** écrit dans un langage à pile appelé [Script](https://en.bitcoin.it/wiki/Script).
La seule instruction de ce langage que j'ai implémentée est **CHECKSIG** qui permet
simplement de vérifier la signature. Cela permet d'utiliser uniquement des transactions
de type [P2PK](https://en.bitcoinwiki.org/wiki/Pay-to-Pubkey_Hash).
Autrement dit, lorsque j'envoie une transaction je ne spécifie pas l'adresse du
destinataire mais sa clé publique.

* **Comment sont générés les tokens de la cryptomonnaie ?**
Les tokens sont uniquement générés lors du minage d'un nouveau bloc.
Lorsqu'un mineur crée un bloc il y ajoute une transaction octroyant 50 BTC
à la clé publique pour laquelle il travaille.

* **Comment est miné le bloc genesis (bloc de départ) ?**
Étant donné, que personne ne détient de tokens au départ comment remplir le bloc genesis ?
J'ai préféré ne pas générer magiquement de l'argent dans le bloc genesis.
J'ai donc créé un type de transaction vide. Lorsque les mineurs reçoivent 2 transactions
vides ils commencent à miner et génèrent le bloc initial. Au fur et à mesure
les récompenses de minage génèrent la cryptomonnaie qui peut être échangée
dans de vraies transactions.

# Environnement virtuel
Les programmes de ce projet s'exécutent dans un environnement virtuel Python.
```shell
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Pour rendre disponible le module **mini_btc** il faut l'ajouter au **PYTHONPATH**.
```shell
cd mini-btc
export PYTHONPATH=$(pwd)
```

# Exécution des tests
Les tests permettent de s'assurer du bon fonctionnement de chacune des classes.
* **test_node.py**: Classe Node.
* **test_fullnode.py**: Classe FullNode.
* **test_miner[12].py**: Classes Miner et Wallet.

Le fichier **test_miner1.py** teste un scénario de transactions entre 2 porte-feuilles.
Le fichier **test_miner2.py** teste le passage à l'échelle d'un réseau de 6 mineurs
recevant 32 transactions vides qui doivent donc miner 16 blocs (2 transactions par bloc).
```shell
cd mini-btc
python tests/test_node.py
python tests/test_fullnode.py
python tests/test_miner1.py
python tests/test_miner2.py
```

# Interface CLI
J'ai réalisé une interface en ligne de commande pour les classes Wallet et Miner
afin de pouvoir expérimenter interactivement le fonctionnement de la blockchain.
```shell
python cli/wallet.py --help
```
```
usage: wallet.py [-h] [-w WALLET_FILE] [-lh LISTEN_HOST] [-lp LISTEN_PORT] [-rh REMOTE_HOST] -rp REMOTE_PORT [-v VERBOSE]

Porte-feuille Mini BTC en ligne de commandes.

optional arguments:
  -h, --help            show this help message and exit
  -w WALLET_FILE, --wallet-file WALLET_FILE
                        Chemin du fichier binaire contenant la clé privée du porte-feuille.
  -lh LISTEN_HOST, --listen-host LISTEN_HOST
                        Adresse d'écoute du porte-feuille par défaut localhost.
  -lp LISTEN_PORT, --listen-port LISTEN_PORT
                        Port d'écoute du porte-feuille par défaut 8000.
  -rh REMOTE_HOST, --remote-host REMOTE_HOST
                        Adresse du noeud auquel se connecter par défaut localhost.
  -rp REMOTE_PORT, --remote-port REMOTE_PORT
                        Port d'écoute du noeud auquel se connecter requis.
  -v VERBOSE, --verbose VERBOSE
                        Niveau de verbosité entre 0 et 2.
```

```shell
python cli/miner.py --help
```
```
usage: miner.py [-h] -p PUBKEY [-lh LISTEN_HOST] [-lp LISTEN_PORT] [-rh REMOTE_HOST] [-rp REMOTE_PORT] [-n MAX_NODES] [-bs BLOCK_SIZE] [-d DIFFICULTY] [-v VERBOSE]

Daemon de minage de Mini BTC.

optional arguments:
  -h, --help            show this help message and exit
  -p PUBKEY, --pubkey PUBKEY
                        Clé publique pour la récompense de minage requis.
  -lh LISTEN_HOST, --listen-host LISTEN_HOST
                        Adresse d'écoute par défaut localhost.
  -lp LISTEN_PORT, --listen-port LISTEN_PORT
                        Port d'écoute par défaut 8001.
  -rh REMOTE_HOST, --remote-host REMOTE_HOST
                        Adresse du noeud auquel se connecter par défaut localhost.
  -rp REMOTE_PORT, --remote-port REMOTE_PORT
                        Port d'écoute du noeud auquel se connecter. Ne pas préciser si premier noeud du réseau.
  -n MAX_NODES, --max-nodes MAX_NODES
                        Nombre maximum de noeuds voisins actifs à conserver par défaut 10.
  -bs BLOCK_SIZE, --block-size BLOCK_SIZE
                        Nombre de transactions d'un bloc par défaut 3
  -d DIFFICULTY, --difficulty DIFFICULTY
                        Difficulté du minage par défaut 5.
  -v VERBOSE, --verbose VERBOSE
                        Niveau de verbosité entre 0 et 2.
```

# Exemple d'utilisation
On peut créer un nouveau porte-feuille de la manière suivante.
```shell
python cli/wallet.py -lp 8000 -rp 8001
```
```
Namespace(listen_host='localhost', listen_port=8000, remote_host='localhost', remote_port=8001, verbose=0, wallet_file=None)

Avez-vous déjà un porte-feuille (Y/n) ? n
Nom de fichier: wallets/alice.bin
Address: 668wc7STftWcCMUR8o9G62epry1GCDc5PiMnWmXySzW8
Public Key: BQfcHxQKFtLLEA9o2azM9N2owM1eaArtwEPJYtguXQPyUohbFubHLjBsb3zQuQSgCEnJ5ZL87yKZ2mZomnKasa7HGgGHG7Rabzo9PjaAt4R6h8RyWRUtSHQCAArqqXagy7rTpfDi4BKoSXcpWsNgfnjBttcd3rbdBxrL9pGHZvPP7vsA2cPPYW1k2LNezr2MW6NSWRmevXYYbq9Ly9WgKWUTXx6yhYTiuWZMG4P8xCNwDqXZPDwUWhcwV5Bf4w4V9kodG9yiJnxRax4bF4CzveJoR68ehYaF1ePNMcnA8cR1SPFTpMJLnQXNv35hGwbz2PRQ4yFPfrYiwLEk1yoaYKWisZj9QyKCnqxRxrGW36TtuBLhksQoBnEkddginsDYezxFG7WZtbwuQWBQzohmTBWd51f9BK3koHrZpUPXrvhgJchmKcqdbH2YRoyMRNSAkADyLBoPphdvbPNEBaHKoDjXNnLXe5ZBEWxeW3qdrXTsPRXmhLYbZ2HbKoAiAg1mWcSqSpZZLV89xJXP1p6Wb1TDAZm8BGLFs9iCLMPZcGzBZ2cPqszor7b8ZngEYDznvKBDbkebq927fWWKwMEcBnLu9KrZg
```

On instancie un réseau de 2 noeuds en ouvrant 2 terminaux séparés.
La récompense de minage dans les deux cas ira à la clé publique de Alice.
Le premier noeud n'est relié à aucun autre pour le moment.
```shell
python cli/miner.py -lp 8001 -p BQfcHxQKFtLLEA9o2azM9N2owM1eaArtwEPJYtguXQPyUohbFubHLjBsb3zQuQSgCEnJ5ZL87yKZ2mZomnKasa7HGgGHG7Rabzo9PjaAt4R6h8RyWRUtSHQCAArqqXagy7rTpfDi4BKoSXcpWsNgfnjBttcd3rbdBxrL9pGHZvPP7vsA2cPPYW1k2LNezr2MW6NSWRmevXYYbq9Ly9WgKWUTXx6yhYTiuWZMG4P8xCNwDqXZPDwUWhcwV5Bf4w4V9kodG9yiJnxRax4bF4CzveJoR68ehYaF1ePNMcnA8cR1SPFTpMJLnQXNv35hGwbz2PRQ4yFPfrYiwLEk1yoaYKWisZj9QyKCnqxRxrGW36TtuBLhksQoBnEkddginsDYezxFG7WZtbwuQWBQzohmTBWd51f9BK3koHrZpUPXrvhgJchmKcqdbH2YRoyMRNSAkADyLBoPphdvbPNEBaHKoDjXNnLXe5ZBEWxeW3qdrXTsPRXmhLYbZ2HbKoAiAg1mWcSqSpZZLV89xJXP1p6Wb1TDAZm8BGLFs9iCLMPZcGzBZ2cPqszor7b8ZngEYDznvKBDbkebq927fWWKwMEcBnLu9KrZg
```

Le second noeud est connecté au précédent.
```shell
python cli/miner.py -lp 8002 -rp 8001 -p BQfcHxQKFtLLEA9o2azM9N2owM1eaArtwEPJYtguXQPyUohbFubHLjBsb3zQuQSgCEnJ5ZL87yKZ2mZomnKasa7HGgGHG7Rabzo9PjaAt4R6h8RyWRUtSHQCAArqqXagy7rTpfDi4BKoSXcpWsNgfnjBttcd3rbdBxrL9pGHZvPP7vsA2cPPYW1k2LNezr2MW6NSWRmevXYYbq9Ly9WgKWUTXx6yhYTiuWZMG4P8xCNwDqXZPDwUWhcwV5Bf4w4V9kodG9yiJnxRax4bF4CzveJoR68ehYaF1ePNMcnA8cR1SPFTpMJLnQXNv35hGwbz2PRQ4yFPfrYiwLEk1yoaYKWisZj9QyKCnqxRxrGW36TtuBLhksQoBnEkddginsDYezxFG7WZtbwuQWBQzohmTBWd51f9BK3koHrZpUPXrvhgJchmKcqdbH2YRoyMRNSAkADyLBoPphdvbPNEBaHKoDjXNnLXe5ZBEWxeW3qdrXTsPRXmhLYbZ2HbKoAiAg1mWcSqSpZZLV89xJXP1p6Wb1TDAZm8BGLFs9iCLMPZcGzBZ2cPqszor7b8ZngEYDznvKBDbkebq927fWWKwMEcBnLu9KrZg
```

On ouvre le porte-feuille de Alice. Notez que `rlwrap` est optionnel.
```shell
rlwrap python cli/wallet.py -w wallets/alice.bin -lp 8000 -rp 8001
```

Un prompt s'affiche et vous pouvez taper des commandes interactivement.
```
Namespace(listen_host='localhost', listen_port=8000, remote_host='localhost', remote_port=8001, verbose=0, wallet_file='wallets/alice.bin')

Address: 668wc7STftWcCMUR8o9G62epry1GCDc5PiMnWmXySzW8
Public Key: BQfcHxQKFtLLEA9o2azM9N2owM1eaArtwEPJYtguXQPyUohbFubHLjBsb3zQuQSgCEnJ5ZL87yKZ2mZomnKasa7HGgGHG7Rabzo9PjaAt4R6h8RyWRUtSHQCAArqqXagy7rTpfDi4BKoSXcpWsNgfnjBttcd3rbdBxrL9pGHZvPP7vsA2cPPYW1k2LNezr2MW6NSWRmevXYYbq9Ly9WgKWUTXx6yhYTiuWZMG4P8xCNwDqXZPDwUWhcwV5Bf4w4V9kodG9yiJnxRax4bF4CzveJoR68ehYaF1ePNMcnA8cR1SPFTpMJLnQXNv35hGwbz2PRQ4yFPfrYiwLEk1yoaYKWisZj9QyKCnqxRxrGW36TtuBLhksQoBnEkddginsDYezxFG7WZtbwuQWBQzohmTBWd51f9BK3koHrZpUPXrvhgJchmKcqdbH2YRoyMRNSAkADyLBoPphdvbPNEBaHKoDjXNnLXe5ZBEWxeW3qdrXTsPRXmhLYbZ2HbKoAiAg1mWcSqSpZZLV89xJXP1p6Wb1TDAZm8BGLFs9iCLMPZcGzBZ2cPqszor7b8ZngEYDznvKBDbkebq927fWWKwMEcBnLu9KrZg

Bienvenue sur le porte-feuille Mini BTC.
Tapez help pour voir la liste des commandes.

> help

* help: Affiche la liste des commandes disponibles.

* update_balance: Met à jour les UTXO du porte-feuille.

* get_balance: Affiche le solde du porte-feuille.
Note: Mettre à jour les UTXO au préalable.

* transfer <pubkey> <value>: Transfère la somme <value> à <pubkey>.
Note: Mettre à jour les UTXO avant et après le transfert.

* exit: Quitte le porte-feuille.
```

Pour connaître le solde de votre porte-feuille pensez toujours à mettre à jour
vos UTXO avec `update_balance` avant d'appeler `get_balance`.
De même avant et après un transfert il faut toujours appeler `update_balance`.
```
> update_balance
SYNC
> get_balance
0 BTC
```

Pour créer le premier bloc il faut commencer par envoyer 2 transactions vides.
```
> transfer
SUCCESS
> transfer
SUCCESS
```

Une fois que l'un des noeuds a miné le bloc genesis on constate que Alice a 50 BTC.
```
> update_balance
SYNC
> get_balance
50 BTC
```

On ne peut pas effectuer une transaction à soi-même. Si on le fait elle sera
invalidée par le mineurs et ne sera jamais incluse dans un bloc.
Nous allons à présent envoyer 10 BTC à Bob depuis le porte-feuille d'Alice.
```
> update_balance
SYNC
> transfer BQfcHxQKFtMcdUYkvCe4bGZfDgcKVLCyGZfDaFGRSWG11zSMLv9jcPaNEMKUq47HD51F7QzjjrVHi79RZ6D9zSVnT7mVWSSAQ6bXtVGQ4MaYuWrXc2ECgcVgcQytkPs2SkTnSx5po3YybGvRQzSbLcn2Zw6PxjtWZMUYwGPUaNSVYrmaXKeMLgdfA4FrDYHkYJgErAfCkJ9FbMN6ov4UtdfxoGNN6pZDfgh26TPLu5eCj6rBMm8rSwqkyzYBrndC8Nt9iLkwh9VoHRg34Y2cr7DB4fJVMvm29L2X2ETo7ZYipv7LwNg6j6t2smhh7t56WdcPcs2KbHuzhPk2DaFzZWE8BkN7PQeQqA27swWd5frVeuaBj13nvTLuafjhFUGENH2aDZsHGGNvVZdanaRDp3Kju53KTswPDoYRd8bAaJiZE9jQYhqjTScVc3wfRtRMJnVsFUsWLEBpBFkXRLoNPeQdwNy4HD7NrTZGaWBSvknHXaQP9ZSzqsY2Wkb8VMY7uFyjLVeD3u7AA5eZ8gBBoXe7tbwvwkbrwn7kPkdAoiuAroVwGmmVQo4oujpkyR8UMsXbimXT2XSVQXPmXu1sL2KKTs6YM 10
SUCCESS
> transfer
> update_balance
SYNC
> get_balance
90 BTC
```
Alice a maintenant 90 BTC car elle a gagné 50 BTC de récompense lors du minage
du 2ème bloc.

```shell
rlwrap python cli/wallet.py -w wallets/bob.bin -lp 8003 -rp 8002
```
On vérifie que Bob a bien reçu les 10 BTC.
```
Namespace(listen_host='localhost', listen_port=8003, remote_host='localhost', remote_port=8002, verbose=0, wallet_file='wallets/bob.bin')

Address: GstPfYgdpF1swfqKWRygoRHavsCtozHaBodZEdUA9bMt
Public Key: BQfcHxQKFtMcdUYkvCe4bGZfDgcKVLCyGZfDaFGRSWG11zSMLv9jcPaNEMKUq47HD51F7QzjjrVHi79RZ6D9zSVnT7mVWSSAQ6bXtVGQ4MaYuWrXc2ECgcVgcQytkPs2SkTnSx5po3YybGvRQzSbLcn2Zw6PxjtWZMUYwGPUaNSVYrmaXKeMLgdfA4FrDYHkYJgErAfCkJ9FbMN6ov4UtdfxoGNN6pZDfgh26TPLu5eCj6rBMm8rSwqkyzYBrndC8Nt9iLkwh9VoHRg34Y2cr7DB4fJVMvm29L2X2ETo7ZYipv7LwNg6j6t2smhh7t56WdcPcs2KbHuzhPk2DaFzZWE8BkN7PQeQqA27swWd5frVeuaBj13nvTLuafjhFUGENH2aDZsHGGNvVZdanaRDp3Kju53KTswPDoYRd8bAaJiZE9jQYhqjTScVc3wfRtRMJnVsFUsWLEBpBFkXRLoNPeQdwNy4HD7NrTZGaWBSvknHXaQP9ZSzqsY2Wkb8VMY7uFyjLVeD3u7AA5eZ8gBBoXe7tbwvwkbrwn7kPkdAoiuAroVwGmmVQo4oujpkyR8UMsXbimXT2XSVQXPmXu1sL2KKTs6YM

Bienvenue sur le porte-feuille Mini BTC.
Tapez help pour voir la liste des commandes.

> update_balance
SYNC
> get_balance
10 BTC
```

# Arbres de Merkle
TODO
