import socket, threading, time
from mini_btc.utils import send, recv, logging
from typing import Union


class Node:
    """
    Noeud du réseau pair à pair agissant à la fois comme un client et un serveur.
    Les communications utilisent des sockets temporaires unidirectionnels.
    """
    def __init__(self, listen_host: str, listen_port: int,
        remote_host: str = None, remote_port: int = None, max_nodes: int = 10,
        verbose: int = 2):
        """
        Lorsque un noeud est créé il doit se connecter à un noeud du réseau.
        préexistant. Si c'est le premier alors il n'y a pas besoin de préciser
        de noeud auquel se connecter.

        :param listen_host: Adresse d'écoute du noeud.
        :param listen_port: Port associé à cette adresse.
        :param remote_host: Adresse du noeud auquel se connecter.
        :param remote_port: Port associé à cette adresse.
        :param max_nodes: Nombre maximum de voisins actifs à conserver.
        :param verbose: Niveau de verbosité entre 0 et 2.
        """
        self.host = listen_host
        self.port = listen_port
        self.name = f"{self.host}:{self.port}"

        assert verbose in [0, 1, 2]
        self.verbose = verbose

        # Identifiants des paquets reçus
        self.packet_ids = set()
        # Verrou sur packet_ids
        self.lock_packet_ids = threading.Lock()

        # Ensemble des noeuds voisins actifs
        self.nodes = set()
        self.max_nodes = max_nodes
        if remote_host is not None and remote_port is not None:
            self.nodes.add((remote_host, remote_port))

        # Socket d'écoute des connexions entrantes
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((listen_host, listen_port))
        # Le serveur a un buffer de 100 connexions
        self.sock.listen(100)

    def __broadcast(self, pck: object):
        """
        Diffusion sur le réseau d'un paquet.

        :param pck: Objet Python contenant le champ id.
        """
        connection_refused = False

        # On ne renvoie pas si on a déjà envoyé pour éviter les cycles
        self.lock_packet_ids.acquire()
        if pck["id"] not in self.packet_ids:
            # Il faudrait vider cet ensemble après un certain temps
            self.packet_ids.add(pck["id"])
            self.lock_packet_ids.release()

            # Exécution de la callback sur le corps du paquet
            self._broadcast_callback(pck["host"], pck["port"], pck["id"], pck["body"].copy())

            for host, port in self.nodes.copy():
                try:
                    send(host, port, pck, ignore_errors=False)
                # Le noeud voisin est inactif
                except ConnectionRefusedError:
                    connection_refused = True
                    self.nodes.remove((host, port))
        else:
            self.lock_packet_ids.release()

        # Recherche de nouveaux voisins
        if connection_refused:
            self.connect()

    def __wait(self):
        """
        Fonction appelée par un thread principal permettant l'écoute des
        connexions entrantes en provenance des autres noeuds du réseau.

        Lorsqu'un paquet arrive il est alors traité dans un thread séparé pour
        ne pas bloquer le thread principal d'écoute.
        """
        while True:
            try:
                # Attente de clients
                sock, ip_client = self.sock.accept()
            # Le socket a été fermé
            except OSError:
                break

            # On traite la requête du client dans un thread séparé
            threading.Thread(target=self.__packet_callback, args=(sock,)).start()

    def __packet_callback(self, sock: socket.socket):
        """
        Fonction appelée dans un thread lors de la réception d'un paquet.
        Elle gère différentes en-têtes de paquet.

        CONNECT: Première demande de connexion d'un noeud.
        CONNECT_ACCEPTED: Connexion d'un noeud acceptée.
        BROADCAST: Diffusion d'un paquet sur le réseau.
        PRIVATE: Paquet privé à ne pas diffuser.
        """
        # Réception du paquet
        pck = recv(sock)
        sock.close()

        if self.verbose == 1:
            log = pck["header"]
            if "host" in pck and "port" in pck:
                log += f" from {pck['host']}:{pck['port']}"
            if "body" in pck and "request" in pck["body"]:
                log += f" {pck['body']['request']}"
            self.logging(log)

        elif self.verbose == 2:
            self.logging(pck)

        # Demande de connexion au réseau
        if "CONNECT" == pck["header"]:
            # Le format JSON ne connaît que les listes pas les ensembles
            rpck = {"header": "CONNECT_ACCEPTED", "nodes": list(self.nodes)}
            send(pck["host"], pck["port"], rpck)

            # Notification du nouvel arrivant à tous les noeuds voisins
            # Attention: Ce n'est pas un broadcast !
            rpck["nodes"] = [(pck["host"], pck["port"])]
            for host, port in self.nodes.copy():
                send(host, port, rpck)

            # Enregistrement du nouvel arrivant si le nombre de connexions
            # actives n'est pas dépassé
            if len(self.nodes) < self.max_nodes:
                self.nodes.add((pck["host"], pck["port"]))

        # Réception d'une liste de noeuds
        elif "CONNECT_ACCEPTED" == pck["header"]:
            nodes = set([tuple(node) for node in pck["nodes"]])
            while len(self.nodes) < self.max_nodes and len(nodes) > 0:
                node = nodes.pop()
                # On ne s'ajoute pas soi-même à l'ensemble des noeuds voisins
                if (self.host, self.port) != node:
                    self.nodes.add(node)

        # Réception d'un paquet à diffuser
        elif "BROADCAST" == pck["header"]:
            # Diffusion du paquet sur le réseau
            self.__broadcast(pck)

        # Paquet privé à ne pas diffuser
        elif "PRIVATE" == pck["header"]:
            self._private_callback(pck["host"], pck["port"], pck["body"].copy())

    def _broadcast_callback(self, host: str, port: int, id: str, body: object):
        """
        Fonction appelée sur le corps d'un paquet diffusé sur le réseau.
        Cette fonction peut être personnalisée par héritage.
        Garantie: Un appel au plus par "id" de paquet.

        :param host: Adresse du noeud expéditeur.
        :param port: Port associée à cette adresse.
        :param id: Identifiant du paquet.
        :param body: Objet Python du corps du paquet.
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
        pass

    def logging(self, msg: Union[str, object]):
        """
        Affichage d'un message dans la sortie standard.

        :param msg: Message à afficher.
        """
        logging(f"<{self.name}> " + str(msg))

    def connect(self):
        """
        Demande de connexion aux noeuds voisins pour mettre à jour l'ensemble
        des noeuds voisins actifs.
        """
        for host, port in self.nodes.copy():
            pck = {"header": "CONNECT", "host": self.host, "port": self.port}
            send(host, port, pck)

    def start(self):
        """
        Démarre le noeud en le connectant au réseau.
        """
        # Attente de connexions
        threading.Thread(target=self.__wait).start()

        # Récupération de la liste des noeuds voisins
        self.connect()

    def shutdown(self):
        """
        Éteins le noeud en lui indiquant d'arrêter d'écouter les connexions entrantes.
        """
        self.sock.shutdown(socket.SHUT_RDWR)

    def broadcast(self, body: object):
        """
        Diffusion sur le réseau d'un objet Python.
        Cet objet sera encapsulé dans un paquet de la couche pair à pair.
        Le champ "id" est automatiquement ajouté à cet objet pour identifier
        la requête. Il s'agit du même identifiant que celui du paquet.

        :param body: Objet Python sérialiable en JSON.
        """
        # On suppose qu'un noeud ne peut pas envoyer plusieurs paquets au même moment
        id = f"{self.name}#{time.time()}"
        pck = {"header": "BROADCAST", "host": self.host, "port": self.port, "id": id, "body": body}
        if self.verbose == 2: self.logging(pck["body"])
        self.__broadcast(pck)

    def send(self, remote_host: str, remote_port: int, body: object):
        """
        Envoi d'un paquet privé à un seul noeud.
        Les champs "host" et "port" indiquant l'expéditeur sont automatiquement
        ajoutés au corps du paquet.

        :param remote_host: Adresse du noeud auquel envoyer le paquet.
        :param remote_port: Port associé à cette adresse.
        :param body: Objet Python sérialiable en JSON.
        """
        pck = {"header": "PRIVATE", "host": self.host, "port": self.port, "body": body}
        if self.verbose == 2: self.logging(pck["body"])
        send(remote_host, remote_port, pck)
