import threading, random
from mini_btc import FullNode
from mini_btc.utils import sha256, json_decode


class Miner(FullNode):
    """
    Noeud de la BlockChain capable de miner des blocs.
    C'est une extension de FullNode.
    """
    def __init__(self, listen_host: str, listen_port: int,
        remote_host: str = None, remote_port: int = None, max_nodes: int = 10,
        block_size: int = 3, difficulty: int = 5):
        """
        Création d'un mineur appartenant à la BlockChain.

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
        super().__init__(listen_host, listen_port, remote_host, remote_port,
            max_nodes, block_size, difficulty)

        self.is_mining = False
        self.mining_cond = threading.Condition()

    def start(self):
        """
        Démarre le mineur en le connectant au réseau.
        """
        super().start()
        threading.Thread(target=self.__mine_routine).start()

    def _transact_callback(self, host: str, port: int, body: object):
        """
        Fonction appelée lors de la réception d'une transaction.

        :param host: Adresse du noeud expéditeur.
        :param port: Port associée à cette adresse.
        :param body: Objet Python du corps du paquet.
        """
        # Réveil du thread de minage
        # Il vérifie en interne s'il peut miner
        with self.mining_cond:
            self.mining_cond.notify_all()

    def _delete_trans(self, trans: set):
        """
        Supprime les transactions en entrée du buffer.

        :param trans: Transactions à supprimer
        """
        super()._delete_trans(trans)

        # Arrêt du minage du bloc courant
        # Le minage reprend automatiquement s'il y a assez de transactions
        self.is_mining = False

    def __mine(self, block: object):
        """
        Minage d'un bloc en incrémentant le nonce.

        :param block: Bloc à miner.
        """
        while self.is_mining and not self._check_block(block):
            block["nonce"] += 1

    def __mine_routine(self):
        """
        Routine de minage à appeler dans un thread.
        Lorsque le bloc est résolu il est automatiquement soumis au réseau.
        Pour indiquer au mineur de changer de bloc à miner il faut assigner
        self.is_mining = False
        """
        block = None
        while True:
            with self.mining_cond:
                # On démarre le minage si on a reçu suffisamment de transactions
                while len(self.buf_trans) < self.block_size:
                    # Attente passive
                    self.mining_cond.wait()

            # Activation du minage
            self.is_mining = True

            # Construction d'un bloc à miner
            trans = random.sample(self.buf_trans, self.block_size)
            encoded_trans = trans.copy()
            decoded_trans = [json_decode(x) for x in trans]
            block = {
                "index": len(self.ledger),
                "hash": None if len(self.ledger) == 0 else sha256(self.ledger[-1]),
                "nonce": random.randint(0, 1_000_000_000),
                "trans": decoded_trans
            }

            # Minage du bloc
            self.__mine(block)

            # Si on a gagné la compétition
            if self.is_mining:
                # Enregistrement du bloc dans le registre
                self.ledger.append(block)
                # On retire les transactions utilisées du buffer
                super()._delete_trans(encoded_trans)
                # Soumission du bloc
                self.submit_block(block)

    def submit_block(self, block: object):
        """
        Soumission d'un bloc au réseau de la BlockChain.

        :param block: Objet Python du bloc à soumettre.
        """
        req = {"request": "SUBMIT_BLOCK", "block": block}
        self.broadcast(req)

    def genesis(self):
        """
        Construit, mine et soumet un bloc genesis servant de racine à la BlockChain.
        """
        block = {"index": 0, "hash": None, "nonce": 0, "trans": []}
        self.is_mining = True
        self.__mine(block)
        self.ledger.append(block)
        self.submit_block(block)
