from mini_btc import Node
import Crypto.Random
from Crypto.PublicKey import RSA
from mini_btc.utils import rsa_publickey
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

    @staticmethod
    def create(output_file: str):
        """
        Création d'un nouveau porte-feuille. On génère une clé privée RSA aléatoire.
        La méthode est simplifiée par rapport au bitcoin.

        :param output_file: Fichier où stocker la clé privée en binaire.
        """
        private_key = RSA.generate(1024, Crypto.Random.new().read)
        public_key, address = rsa_publickey(private_key)

        print(f"Address: {address}")
        print(f"Public Key: {public_key}")

        with open(output_file, 'wb') as f:
            f.write(private_key.exportKey("DER"))

    def _import(self, wallet_file: str):
        """
        Importe un porte-feuille existant.

        :param wallet_file: Chemin du fichier de la clé privée.
        """
        with open(wallet_file, 'rb') as f:
            self._private_key = RSA.importKey(f.read())
        self.public_key, self.address = rsa_publickey(self._private_key)

    def connect(self):
        """
        Désactivation de la récupération de la liste de voisins.
        La wallet n'est connecté qu'à un seul noeud.
        """
        pass

    def transfer(self, dest: str, amount: int):
        """
        Soumission d'une transaction au réseau.
        Note: Dans la réalité il faudrait travailler avec de la cryptographie
        symétrique. Ici on ne le fait pas par souci de simplification.

        :param dest: Adresse du destinataire.
        :param amount: Montant de la transaction.
        """
        req = {"request": "TRANSACT", "from": self.address, "to": dest, "amount": amount}
        self.broadcast(req)
