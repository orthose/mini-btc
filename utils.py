import socket, json
from typing import Callable, Tuple, Union
import datetime as dt


def create_sock(host: str, port: int) -> socket.socket:
    """
    Crée une prise bidirectionnelle vers un noeud.

    :param host: Adresse du noeud.
    :param port: Port associé à cette adresse.
    :return: Prise connectée.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.connect((host, port))
    return sock


def pipe_sock(sock: socket.socket) -> Tuple[Callable[[object], bytes], Callable[[int], object]]:
    """
    Permet d'échanger des objets entre noeuds au travers d'une prise.

    :param sock: Prise connectée à un noeud.
    :return: Fonctions pour envoyer et recevoir un objet Python sérialisable en JSON.
    """
    send = lambda obj: sock.send(json.dumps(obj).encode('utf-8'))
    recv = lambda bufsize=1024: json.loads(sock.recv(bufsize).decode('utf-8'))
    return send, recv


def logging(msg: Union[str, object]):
    """
    Affichage dans la sortie standard d'un message précédé par sa date d'émission.

    :param msg: Message à afficher.
    """
    print(f"[{dt.datetime.now().strftime('%Y-%d-%m %H:%M:%S')}] {msg}")
