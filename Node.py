import socket, threading
from utils import send, recv, logging
from typing import Union


class Node:
    """
    Noeud du réseau pair à pair agissant à la fois comme un client et un serveur.
    Les communications utilisent des sockets temporaires unidirectionnels.
    """
    def __init__(self, listen_host: str, listen_port: int,
        remote_host: str = None, remote_port: int = None, num_nodes: int = 10,
        verbose: bool = True):
        """
        Lorsque un noeud est créé il doit se connecter à un noeud déjà existant
        du réseau. Si c'est le premier alors il n'y a pas besoin de préciser
        de noeud auquel se connecter.

        :param listen_host: Adresse d'écoute noeud.
        :param listen_port: Port associé à cette adresse.
        :param remote_host: Adresse du noeud auquel se connecter.
        :param remote_port: Port associé à cette adresse.
        :param num_nodes: Nombre maximum de voisins actifs à conserver.
        :param verbose: Si True alors affichage des logs dans la console.
        """
        self.host = listen_host
        self.port = listen_port
        self.verbose = verbose

        self.nodes = set() # Ensemble des noeuds voisins
        self.num_nodes = num_nodes
        if remote_host is not None and remote_port is not None:
            self.nodes.add((remote_host, remote_port))

        # Socket d'écoute des connexions entrantes
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((listen_host, listen_port))
        self.sock.listen(100) # Le serveur peut traiter jusqu'à 100 connexions

    def _wait(self):
        # Attente de clients
        while True:
            sock, ip_client = self.sock.accept()
            # On traite la requête du client dans un thread séparé
            threading.Thread(target=self._exec_req, args=(sock,)).start()

    def _exec_req(self, sock: socket.socket):
        # Réception de la requête
        req = recv(sock)
        sock.close()
        self.logging(req)

        # Demande de connexion au réseau
        if "CONNECT" == req["header"]:
            # Le format JSON ne connaît que les listes pas les ensembles
            obj = {"header": "CONNECT_ACCEPTED", "nodes": list(self.nodes)}
            send(req["host"], req["port"], obj)

            # Notification du nouvel arrivant à tous les noeuds voisins
            # Attention: Ce n'est pas un broadcast !
            obj["nodes"] = [(req["host"], req["port"])]
            for host, port in self.nodes:
                send(host, port, obj)

            # Enregistrement du nouvel arrivant si le nombre de connexions
            # actives n'est pas dépassé
            if len(self.nodes) < self.num_nodes:
                self.nodes.add((req["host"], req["port"]))

        # Réception d'une liste de noeuds
        elif "CONNECT_ACCEPTED" == req["header"]:
            nodes = set([tuple(node) for node in req["nodes"]])
            while len(self.nodes) < self.num_nodes and len(nodes) > 0:
                self.nodes.add(nodes.pop())
            self.logging(self.nodes)

    def logging(self, msg: Union[str, object]):
        """
        Affichage d'un message dans la sortie standard.

        :param msg: Message à afficher.
        """
        logging(f"<{self.host}:{self.port}> " + str(msg))

    def start(self):
        """
        Démarre le noeud en le connectant au réseau.
        """
        # Attente de connexions
        threading.Thread(target=self._wait).start()

        # Récupération de la liste des noeuds voisins
        for host, port in self.nodes:
            obj = {"header": "CONNECT", "host": self.host, "port": self.port}
            send(host, port, obj)

    def broadcast(self, msg: str):
        pass
