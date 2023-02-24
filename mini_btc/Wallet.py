from mini_btc.utils import \
    dsa_generate, dsa_export, dsa_import, \
    dsa_pubkey, address_from_pubkey, dsa_sign
from mini_btc import Node
from mini_btc import Transaction
from mini_btc import MerkleTree
from typing import Tuple, Union


class Wallet(Node):
    """
    Porte-feuille permettant de communiquer avec un noeud de la BlockChain.
    ATTENTION: Le Wallet doit être connecté à un FullNode ou un Miner.

    Le porte-feuille est un noeud léger. Il stocke le registre des headers de bloc.
    Il ne vérifie pas la BlockChain il fait confiance au FullNode auquel il se connecte.
    """
    def __init__(self, wallet_file: str, listen_host: str, listen_port: int,
        remote_host, remote_port: int, verbose: int = 2):
        """
        :param wallet_file: Chemin du fichier de la clé privée du porte-feuille.
        :param listen_host: Adresse d'écoute du wallet.
        :param listen_port: Port associé à cette adresse.
        :param remote_host: Adresse du noeud auquel se connecter.
        :param remote_port: Port associé à cette adresse.
        :param verbose: Niveau de verbosité entre 0 et 2.
        """
        super().__init__(listen_host, listen_port, remote_host, remote_port,
            max_nodes=1, verbose=verbose)

        self.remote_host, self.remote_port = remote_host, remote_port

        # Chargement du fichier contenant la clé privée
        self._import(wallet_file)

        # Annuaire des adresses
        self.addr = dict()

        # Registre des headers de bloc
        self.ledger = []

        # Transactions non-dépensées
        self.utxo = []

        # Preuves de validation des transactions
        self.proof_tx = dict()

    @staticmethod
    def create(wallet_file: str):
        """
        Création d'un nouveau porte-feuille. On génère une clé privée RSA aléatoire.
        La méthode est simplifiée par rapport au bitcoin.

        :param wallet_file: Fichier où stocker la clé privée en binaire.
        """
        privkey = dsa_generate()
        pubkey, address = dsa_pubkey(privkey)

        dsa_export(privkey, wallet_file)

    def _import(self, wallet_file: str):
        """
        Importe un porte-feuille existant.

        :param wallet_file: Chemin du fichier de la clé privée.
        """
        self._privkey = dsa_import(wallet_file)
        self.pubkey, self.address = dsa_pubkey(self._privkey)

        print(f"Address: {self.address}")
        print(f"Public Key: {self.pubkey}")

    def connect(self):
        """
        Désactivation de la récupération de la liste de voisins.
        La wallet n'est connecté qu'à un seul noeud.
        """
        pass

    def _private_callback(self, host: str, port: int, body: object):
        """
        Fonction appelée sur le corps d'un paquet privé.
        Cette fonction peut être personnalisée par héritage.

        :param host: Adresse du noeud expéditeur.
        :param port: Port associée à cette adresse.
        :param body: Objet Python du corps du paquet.
        """
        # Mise à jour des UTXO du porte-feuille
        if "BALANCE" == body["request"]:
            self.utxo = body["utxo"]

        # Récupération de la blockchain
        elif "LIST_BLOCKS" == body["request"]:
            ledger = []
            for block in body["blocks"]:
                # On ne garde que les headers de bloc
                block.pop("tx")
                # On ne vérifie pas les blocs
                ledger.append(block)
            # On écrase la totalité du registre
            self.ledger = ledger

        elif "PROOF" == body["request"]:
            self.proof_tx[body["txid"]] = {"index": body["index"], "proof": body["proof"]}

    def update_balance(self):
        """
        Demande au noeud les UTXO appartenant à l'adresse du porte-feuille
        pour mettre à jour le solde. Requête asynchrone.
        """
        req = {"request": "GET_BALANCE", "address": self.address}
        self.send(self.remote_host, self.remote_port, req)

    def get_balance(self) -> int:
        """
        Donne le solde actuel connu par le porte-feuille.
        Pour mettre à jour le solde il faut appeler au préalable update_balance.

        :return: Entier du solde.
        """
        res = 0
        for tx in self.utxo:
            index = Transaction(tx).find_utxo(self.address)
            if index > -1:
                res += tx["output"][index]["value"]
        return res

    def register(self, name: str, addr: str):
        """
        Enregistrement d'une adresse avec un nom raccourci dans l'annuaire.
        L'adresse peut être une clé publique dans le cas d'un paiement P2PK.

        :param name: Raccourci pour retrouver l'adresse.
        :param addr: Adresse complète à enregistrer.
        """
        self.addr[name] = addr

    def transfer(self, dest_pubkey: str, value: int) -> Union[str, None]:
        """
        Soumission d'une transaction au réseau.

        :param dest_pubkey: Clé publique du destinataire
        ou raccourci présent dans l'annuaire.
        :param value: Montant de la transaction.
        :return: txid si la transaction a été envoyée None sinon.
        """
        # Le transfert est abandonné si pas de UTXO
        if len(self.utxo) == 0: return None

        tx = Transaction()
        input_value = 0; i = 0
        while input_value < value and i < len(self.utxo):
            utxo = self.utxo[i]
            index = Transaction(utxo).find_utxo(self.address)
            hash = utxo.pop("hash")
            sign = dsa_sign(self._privkey, utxo)
            tx.add_input(prevTxHash=hash, index=index, unlock=sign)
            input_value += utxo["output"][index]["value"]; i += 1

        # Le solde est-il suffisant ?
        if input_value < value: return None

        # Suppression des UTXO consommées
        self.utxo = self.utxo[i+1:]

        # UTXO pour le destinataire
        if dest_pubkey in self.addr:
            dest_pubkey = self.addr[dest_pubkey]
        lock = f"{dest_pubkey} CHECKSIG"
        tx.add_output(address=address_from_pubkey(dest_pubkey), value=value, lock=lock)

        # Je me rembourse
        input_value -= value
        if input_value > 0:
            lock = f"{self.pubkey} CHECKSIG"
            tx.add_output(address=address_from_pubkey(self.pubkey), value=input_value, lock=lock)

        tx = tx.to_dict()
        req = {"request": "TRANSACT", "tx": tx}
        self.broadcast(req)

        return tx["hash"]

    def empty_transfer(self) -> Union[str, None]:
        """
        Soumission d'une transaction vide.
        Permet de lancer le minage du premier bloc.

        :return: txid si la transaction a été envoyée None sinon.
        """
        tx = Transaction().to_dict()
        req = {"request": "TRANSACT", "tx": tx}
        self.broadcast(req)

        return tx["hash"]

    def sync_block(self):
        """
        Mise à jour du registre du porte-feuille.
        Les blocs ne sont pas vérifiés.
        """
        req = {"request": "GET_BLOCKS"}
        self.send(self.remote_host, self.remote_port, req)

    def get_proof(self, txid: str):
        """
        Demande une preuve de validation d'une transaction.
        La réception de la preuve est asynchrone.
        Si aucune réponse n'est reçue cela peut signifier que la transaction
        n'est pas encore validée.

        :param txid: Hash de la transaction à prouver.
        """
        req = {"request": "GET_PROOF", "txid": txid}
        self.send(self.remote_host, self.remote_port, req)

    def verify_proof(self, txid: str) -> bool:
        """
        Vérifie une preuve reçue pour une transaction.

        :param txid: Hash de la transaction à vérifer.
        :return: True si transaction validée False sinon.
        """
        res = False

        if txid in self.proof_tx:
            proof = self.proof_tx[txid]
            index = proof["index"]

            # Le registre n'est pas à jour
            if len(self.ledger) <= index:
                return False

            root = self.ledger[index]["root"]
            proof = proof["proof"]
            res = MerkleTree.verify_proof(txid, root, proof)

        return res
