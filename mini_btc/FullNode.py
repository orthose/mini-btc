import threading
from mini_btc import Node
from mini_btc.utils import sha256, send
from mini_btc import Transaction
from mini_btc.script import execute
from typing import Union


class FullNode(Node):
    """
    Noeud de la BlockChain basé sur la couche pair à pair.
    Ce noeud enregistre l'intégralité du registre et le tient à jour.
    """
    def __init__(self, listen_host: str, listen_port: int,
        remote_host: str = None, remote_port: int = None, max_nodes: int = 10,
        block_size: int = 3, difficulty: int = 5):
        """
        Création d'un noeud appartenant à la BlockChain.

        Lorsque un noeud est créé il doit se connecter à un noeud du réseau.
        préexistant. Si c'est le premier alors il n'y a pas besoin de préciser
        de noeud auquel se connecter.

        :param listen_host: Adresse d'écoute noeud.
        :param listen_port: Port associé à cette adresse.
        :param remote_host: Adresse du noeud auquel se connecter.
        :param remote_port: Port associé à cette adresse.
        :param max_nodes: Nombre maximum de voisins actifs à conserver.
        :param block_size: Nombre de transactions d'un bloc.
        :param difficulty: Difficulté du challenge de minage correspondant
        au nombre de 0 attendus en début de hash. Plus ce nombre est élevé
        plus la difficulté est grande.
        """
        # Création du noeud la couche pair à pair
        super().__init__(listen_host, listen_port, remote_host, remote_port,
            max_nodes)

        # Registre pour stocker la liste de blocs
        self.ledger = []
        self.lock_ledger = threading.Lock()
        self.block_size = block_size

        # Tampon des transactions candidates (à inclure dans les prochains blocs)
        self.buf_trans = set()
        # Transactions non-dépensées par adresse
        self.utxo = dict()

        assert difficulty > 0
        self.difficulty = difficulty

    def _broadcast_callback(self, host: str, port: int, id: str, body: object):
        """
        Fonction appelée sur le corps d'un paquet diffusé sur le réseau.
        Cette fonction peut être personnalisée par héritage.
        Garantie: Un appel au plus par "id" de paquet.

        :param host: Adresse du noeud expéditeur.
        :param port: Port associée à cette adresse.
        :param id: Identifiant du paquet.
        :param body: Objet Python du corps du paquet.

        TRANSACT: Traitement d'une transaction.
        SUBMIT_BLOCK: Soumission d'un bloc résolu.
        """
        # Traitement d'une transaction
        if "TRANSACT" == body["request"]:
            body.pop("request")
            self.buf_trans.add(Transaction(body["tx"]))
            self._transact_callback(host, port, body)

        # Soumission d'un bloc résolu
        elif "SUBMIT_BLOCK" == body["request"]:
            block = body["block"]

            # Le bloc est-il valide ?
            if self._check_block(block, check_tx=False):
                k = block["index"] # 0-based
                n = len(self.ledger)

                # En retard de 1 bloc
                if k == n:
                    # Ajout du bloc au registre
                    self._add_block(block)

                # En retard de plus de 1 bloc
                elif k > n:
                    req = {"request": "GET_BLOCKS"}
                    super().send(host, port, req)

                # Si pas de retard ne pas prendre en compte le bloc proposé

    def _private_callback(self, host: str, port: int, body: object):
        """
        Fonction appelée sur le corps d'un paquet privé.
        Cette fonction peut être personnalisée par héritage.

        :param host: Adresse du noeud expéditeur.
        :param port: Port associée à cette adresse.
        :param body: Objet Python du corps du paquet.

        GET_BLOCKS: Demande d'une liste de blocs résolus.
        LIST_BLOCKS: Réception d'une liste de blocs résolus.
        """
        # Demande de blocs résolus
        if "GET_BLOCKS" == body["request"]:
            # On envoie la blockchain entière pour simplifier
            req = {"request": "LIST_BLOCKS", "blocks": self.ledger}
            super().send(host, port, req)

        # Réception de blocs résolus
        # Un noeud qui se connecte plus tard peut récupérer toute la blockchain
        elif "LIST_BLOCKS" == body["request"]:
            # Il faut au moins un bloc reçu
            if len(body["blocks"]) == 0:
                return

            # Récupération des anciennes transactions
            old_tx = set()
            for block in self.ledger:
                old_tx.update({Transaction(tx) for tx in block["trans"]})
            # Ajout des anciennes transactions libérées
            self.buf_trans.update(old_tx)

            self.lock_ledger.acquire()

            # Suppression du registre actuel
            # Le premier bloc genesis est particulier: il ne faut pas vérifier le chaînage
            block = body["blocks"][0]
            if not self._check_block(block):
                return
            self.ledger = [block]

            # Reconstruction du registre
            # On suppose que les blocs sont bien ordonnés
            for block in body["blocks"][1:]:
                # Ajout du bloc au registre
                if not self._add_block(block, lock=False): break

            self.lock_ledger.release()

        # Demande de la somme d'argent détenue par une adresse
        elif "GET_BALANCE" == body["request"]:
            address = body["address"]
            utxo = [tx.to_dict() for tx in self.utxo[address]] if address in self.utxo else []
            req = {"request": "BALANCE", "address": address, "utxo": utxo}
            super().send(host, port, req)

    def _delete_trans(self, trans: set):
        """
        Supprime les transactions en entrée du buffer.

        :param trans: Transactions à supprimer
        """
        self.buf_trans.difference_update(trans)

    def _transact_callback(self, host: str, port: int, body: object):
        """
        Fonction appelée lors de la réception d'une transaction.

        :param host: Adresse du noeud expéditeur.
        :param port: Port associée à cette adresse.
        :param body: Objet Python du corps du paquet.
        """
        pass

    def _check_block(self, block: object, check_tx: bool = True) -> bool:
        """
        Vérifie si un bloc est valide.

        :param block: Objet Python du bloc à vérifier.
        :param check_tx: Si True vérifie les transactions du bloc.
        :return: True si valide False sinon.
        """
        # Les champs du bloc sont-ils tous renseignés ?
        res = (len(block) == 4 and "index" in block and "hash" in block
            and "nonce" in block and "trans" in block)

        # Le hash du bloc comprend-il difficulty 0 au début ?
        res = res and '0' * self.difficulty == sha256(block)[0:self.difficulty]

        # Les transactions sont-elles valides ?
        if check_tx:
            # On accepte une seule transaction récompense par bloc
            reward_utxo = False
            for tx in block["trans"]:
                tx = Transaction(tx)

                # Transaction récompense
                if len(tx.input) == 0 and len(tx.output) == 1:
                    # La transaction récompense est-elle valide ?
                    if reward_utxo or tx.output[0]["value"] > 50: return False
                    else: reward_utxo = True

                # Transaction classique
                else:
                    res = res and self.check_tx(tx)
        return res

    def _check_chain(self, block: object) -> bool:
        """
        Vérifie si un bloc peut être ajouté en fin de registre.

        :param block: Objet Python du bloc à vérifier.
        :return: True si valide False sinon.
        """
        return len(self.ledger) == 0 or sha256(self.ledger[-1]) == block["hash"]

    def find_tx(self, txHash: str) -> Union[Transaction, None]:
        """
        Recherche une transaction dans le registre.

        :param txHash: Hash de la transaction.
        :return: Transaction correspondante None si absente.
        """
        for block in self.ledger:
            for tx in block["trans"]:
                if txHash == tx["hash"]:
                    return Transaction(tx)
        return None

    def check_tx(self, tx: Transaction) -> bool:
        """
        Vérifie si une transaction est valide.

        On ne vérifie pas si la transaction est dans le tampon des transactions
        candidates au cas où le noeud ne l'ait pas reçu.

        On ne valide pas les transactions de récompense de minage.
        Ces transactions spéciales sont validées au niveau de self._check_block.

        :param tx: Transaction à vérifier.
        :return: True si valide False sinon.
        """
        # Transaction vide
        if len(tx.input) == 0 and len(tx.output) == 0: return True

        # Transaction classique
        input_value = 0
        # Les entrées sont-elles valides ?
        for intx in tx.input:
            prev_tx = self.find_tx(intx["prevTxHash"])
            # La transaction consommée existe-t-elle dans le registre ?
            if prev_tx is None: return False

            utxo = prev_tx.output[intx["index"]]
            # La UTXO a-t-elle déjà été consommée ?
            if prev_tx not in self.utxo[utxo["address"]]: return False

            # Le déverrouillage a-t-il échoué ?
            if execute(intx["unlock"], utxo["lock"], prev_tx) == "false": return False
            input_value += utxo["value"]

        # La somme en entrée est-elle égale à la somme en sortie ?
        output_value = sum([utxo["value"] for utxo in tx.output])

        # La contrainte d'unicité des adresses en sortie est-elle respectée ?
        nunique = len({utxo["address"] for utxo in tx.output})

        return input_value == output_value and nunique == len(tx.output)

    def _add_block(self, block: object, lock: bool = True) -> bool:
        """
        Ajoute un bloc au registre s'il est valide.

        :param block: Bloc à ajouter au registre.
        :param lock: Verrouillage du registre si True.
        :return: True si le bloc a été ajouté False sinon.
        """
        if lock: self.lock_ledger.acquire()

        # Le bloc est-il valide et suit-il le dernier bloc du registre ?
        res = self._check_block(block) and self._check_chain(block)
        if res:
            # Ajout du bloc au registre
            self.ledger.append(block)

            for tx in block["trans"]:
                # Suppression des UTXO consommées
                for intx in tx["input"]:
                    index = intx["index"]
                    intx = self.find_tx(intx["prevTxHash"])
                    if intx is not None:
                        address = intx.output[index]["address"]
                        # KeyError possible
                        self.utxo[address].remove(intx)

                # Enregistrement des UTXO créées
                for utxo in tx["output"]:
                    address = utxo["address"]
                    if address not in self.utxo:
                        self.utxo[address] = set()
                    self.utxo[address].add(Transaction(tx))

            # Suppression des transactions candidates traitées
            self._delete_trans({Transaction(tx) for tx in block["trans"]})

        if lock: self.lock_ledger.release()

        return res
