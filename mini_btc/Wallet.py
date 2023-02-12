from mini_btc.utils import \
    dsa_generate, dsa_export, dsa_import, \
    dsa_publickey, address_from_publickey, dsa_sign
from mini_btc import Node
from mini_btc import Transaction
from typing import Tuple


class Wallet(Node):
    """
    Porte-feuille permettant de communiquer avec un noeud de la BlockChain.
    ATTENTION: Le Wallet doit être connecté à un FullNode ou un Miner.
    """
    def __init__(self, wallet_file: str, listen_host: str, listen_port: int,
        remote_host, remote_port: int):
        """
        :param wallet_file: Chemin du fichier de la clé privée du porte-feuille.
        :param listen_host: Adresse d'écoute du wallet.
        :param listen_port: Port associé à cette adresse.
        :param remote_host: Adresse du noeud auquel se connecter.
        :param remote_port: Port associé à cette adresse.
        """
        super().__init__(listen_host, listen_port, remote_host, remote_port, max_nodes=1)
        self._import(wallet_file)
        self.utxo = []

    @staticmethod
    def create(wallet_file: str):
        """
        Création d'un nouveau porte-feuille. On génère une clé privée RSA aléatoire.
        La méthode est simplifiée par rapport au bitcoin.

        :param wallet_file: Fichier où stocker la clé privée en binaire.
        """
        private_key = dsa_generate()
        public_key, address = dsa_publickey(private_key)

        print(f"Address: {address}")
        print(f"Public Key: {public_key}")

        dsa_export(private_key, wallet_file)

    def _import(self, wallet_file: str):
        """
        Importe un porte-feuille existant.

        :param wallet_file: Chemin du fichier de la clé privée.
        """
        self._private_key = dsa_import(wallet_file)
        self.public_key, self.address = dsa_publickey(self._private_key)

        print(f"Address: {self.address}")
        print(f"Public Key: {self.public_key}")

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

    def update_balance(self):
        """
        Demande au noeud les UTXO appartenant à l'adresse du porte-feuille
        pour mettre à jour le solde. Requête asynchrone.
        """
        remote_host, remote_port = list(self.nodes)[0]
        req = {"request": "GET_BALANCE", "address": self.address}
        self.send(remote_host, remote_port, req)

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

    def transfer(self, dest_pubkey: str, value: int) -> bool:
        """
        Soumission d'une transaction au réseau.

        :param dest_pubkey: Clé publique du destinataire.
        :param value: Montant de la transaction.
        :return: True si la transaction a été envoyée False sinon.
        """
        # Le transfert est abandonné si pas de UTXO
        if len(self.utxo) == 0: return False

        tx = Transaction()
        input_value = 0; i = 0
        while input_value < value and i < len(self.utxo):
            utxo = self.utxo[i]
            index = Transaction(utxo).find_utxo(self.address)
            hash = utxo.pop("hash")
            sign = dsa_sign(self._private_key, utxo)
            tx.add_input(prevTxHash=hash, index=index, unlock=sign)
            input_value += utxo["output"][index]["value"]

        # Le solde est-il suffisant ?
        if input_value < value: return False

        # Suppression des UTXO consommées
        self.utxo = self.utxo[i+1:]

        # UTXO pour le destinataire
        lock = f"{dest_pubkey} CHECKSIG"
        tx.add_output(address=address_from_publickey(dest_pubkey), value=value, lock=lock)

        # Je me rembourse
        input_value -= value
        if input_value > 0:
            lock = f"{self.public_key} CHECKSIG"
            tx.add_output(address=address_from_publickey(self.public_key), value=input_value, lock=lock)

        req = {"request": "TRANSACT", "tx": tx.to_dict()}
        self.logging(req)
        self.broadcast(req)

        return True

    def empty_transfer(self) -> bool:
        """
        Soumission d'une transaction vide.
        Permet de lancer le minage du premier bloc.

        :return: True si la transaction a été envoyée False sinon.
        """
        tx = Transaction()
        req = {"request": "TRANSACT", "tx": tx.to_dict()}
        self.logging(req)
        self.broadcast(req)

        return True
