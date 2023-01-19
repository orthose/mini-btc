from mini_btc import Node


class Wallet(Node):
    """
    Porte-feuille permettant de communiquer avec un noeud de la BlockChain.
    ATTENTION: Le Wallet doit être connecté à un FullNode ou un Miner.
    """
    def __init__(self, listen_host: str, listen_port: int,
        remote_host, remote_port: int):
        """
        :param listen_host: Adresse d'écoute du wallet.
        :param listen_port: Port associé à cette adresse.
        :param remote_host: Adresse du noeud auquel se connecter.
        :param remote_port: Port associé à cette adresse.
        """
        super().__init__(listen_host, listen_port, remote_host, remote_port, max_nodes=1)

    def connect(self):
        """
        Désactivation de la récupération de la liste de voisins.
        La wallet n'est connecté qu'à un seul noeud.
        """
        pass

    def transact(self, exp: str, dest: str, amount: int):
        """
        Soumission d'une transaction au réseau.
        Note: Dans la réalité il faudrait travailler avec de la cryptographie
        symétrique. Ici on ne le fait pas par souci de simplification.

        :param exp: Nom de l'expéditeur.
        :param dest: Nom du destinataire.
        :param amount: Montant de la transaction.
        """
        req = {"request": "TRANSACT", "from": exp, "to": dest, "amount": amount}
        self.broadcast(req)
