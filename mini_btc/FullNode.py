from mini_btc import Node
from mini_btc.utils import json_encode, sha256, send


class FullNode(Node):
    """
    Noeud de la BlockChain basé sur la couche pair à pair.
    Ce noeud enregistre l'intégralité du registre et le tient à jour.
    """
    def __init__(self, listen_host: str, listen_port: int,
        remote_host: str = None, remote_port: int = None, max_nodes: int = 10,
        block_size: int = 5, difficulty: int = 2):
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

        # Tampon de transactions
        self.buf_trans = set()
        self.block_size = block_size

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
            body["id"] = id
            self.buf_trans.add(json_encode(body))
            self._transact_callback(host, port, body)

        # Soumission d'un bloc résolu
        elif "SUBMIT_BLOCK" == body["request"]:
            block = body["block"]

            # Le bloc est-il valide ?
            if self._check_block(block):
                k = block["index"] # 0-based
                n = len(self.ledger)

                # En retard de 1 bloc
                if k == n:
                    # Le bloc proposé suit-il le dernier bloc ?
                    if self._check_chain(block):
                        self.ledger.append(block)

                # En retard de plus de 1 bloc
                elif k > n:
                    req = {"request": "GET_BLOCKS", "start": n}
                    super().send(host, port, req)

                # Si pas de retard ne pas prendre en compte

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
            req = {"request": "LIST_BLOCKS", "blocks": self.ledger[body["start"]:]}
            super().send(host, port, req)

        # Réception de blocs résolus
        elif "LIST_BLOCKS" == body["request"]:
            # On suppose que les blocs sont bien ordonnés
            for block in body["blocks"]:
                # Le bloc est-il valide et complète-il la blockchain ?
                if self._check_block(block) and self._check_chain(block):
                    # Ajout du bloc dans la blockchain
                    self.ledger.append(block)
                    # Suppression des transactions déjà traitées
                    self.buf_trans.difference_update(set(block["trans"]))

    def _transact_callback(self, host: str, port: int, body: object):
        """
        Fonction appelée lors de la réception d'une transaction.

        :param host: Adresse du noeud expéditeur.
        :param port: Port associée à cette adresse.
        :param body: Objet Python du corps du paquet.
        """
        pass

    def _check_block(self, block: object) -> bool:
        """
        Vérifie si un bloc est valide.

        :param block: Objet Python du bloc à vérifier.
        :return: True si valide False sinon.
        """
        # Les champs du bloc sont-ils tous renseignés ?
        res = (len(block) == 4 and "index" in block and "hash" in block
            and "nonce" in block and "trans" in block)

        # Le hash du bloc comprend-il difficulty 0 au début ?
        res = res and '0' * self.difficulty == sha256(block)[0:self.difficulty]

        return res

    def _check_chain(self, block: object) -> bool:
        """
        Vérifie si un bloc peut être ajouté en fin de registre.

        :param block: Objet Python du bloc à vérifier.
        :return: True si valide False sinon.
        """
        return len(self.ledger) == 0 or sha256(self.ledger[-1]) == body["hash"]
