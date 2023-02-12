from mini_btc.utils import sha256, json_encode
from typing import Tuple
from time import time
from typing import Optional


class Transaction:
    """
    Représentation d'une transaction.

    * Entrées: Les transactions consommées.
    * Sorties: Les UTXO càd les transactions produites.
    * Locktime: Date d'émission de la transaction.
    * Hash: Identification de la transaction.
    """
    def __init__(self, tx: Optional[dict] = None):
        """
        Création d'une transaction.

        :param tx: Initialisation à partir du dictionnaire d'une transaction.
        """
        if tx is None:
            self.input = []
            self.output = []
            self.locktime = time()
        else:
            self.input = tx["input"]
            self.output = tx["output"]
            self.locktime = tx["locktime"]

    def __eq__(self, other: 'Transaction') -> bool:
        return self.to_dict() == other.to_dict()

    def __hash__(self):
        return int.from_bytes(self.to_dict()["hash"].encode("utf-8"), "big")

    def add_input(self, prevTxHash: str, index: int, unlock: str):
        """
        Ajout d'une entrée à la transaction.

        :param prevTxHash: Hash de la transaction consommée.
        :param index: Indice de la sortie de la transaction consommée.
        :param unlock: Argument pour déverrouiller la UTXO désignée.
        """
        self.input.append({"prevTxHash": prevTxHash, "index": index, "unlock": unlock})

    def add_output(self, address: str, value: int, lock: str):
        """
        Ajout d'une sortie à la transaction.

        :param address: Adresse de destination.
        :param value: Somme à envoyer à cette adresse.
        :param lock: Programme de verrouillage de la UTXO.
        """
        self.output.append({"address": address, "value": value, "lock": lock})

    def find_utxo(self, address: str) -> int:
        """
        Recherche la UTXO appartenant à une adresse.
        Il n'y a qu'une unique UTXO par adresse et par transaction.

        :param address: Adresse à chercher.
        :return: L'indice à partir de 0 dans self.output -1 si adresse absente.
        """
        for (index, utxo) in enumerate(self.output):
            if address == utxo["address"]:
                return index
        return -1

    def to_dict(self) -> dict:
        """
        Représentation sous forme de dictionnaire de la transaction.

        :return: Dictionnaire de la transaction.
        """
        tx = {"locktime": self.locktime, "input": self.input, "output": self.output}
        tx["hash"] = sha256(tx)
        return tx

    def raw_format(self) -> bytes:
        """
        Représentation binaire de la transaction.

        :return: Chaîne binaire de la transaction.
        """
        return json_encode(self.to_dict())
