from mini_btc.utils import sha256, json_encode
from time import time


class Transaction:
    """
    Représentation d'une transaction.

    * Entrées: Les transactions consommées.
    * Sorties: Les UTXO càd les transactions produites.
    * Locktime: Date d'émission de la transaction.
    * Hash: Identification de la transaction.
    """
    def __init__(self):
        self.input = []
        self.output = []
        self.locktime = time()

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

    def to_dict(self) -> dict:
        """
        Représentation sous forme de dictionnaire de la transaction.

        :return: Dictionnaire de la transaction.
        """
        res = {"locktime": self.locktime, "input": self.input, "output": self.output}
        res["hash"] = sha256(res)
        return res

    def raw_format(self) -> bytes:
        """
        Représentation binaire de la transaction.

        :return: Chaîne binaire de la transaction.
        """
        return json_encode(self.to_dict())
