import socket, json, hashlib
from typing import Callable, Tuple, Union
import datetime as dt


def json_encode(obj: object) -> bytes:
    return json.dumps(obj).encode('utf-8')

def json_decode(obj: bytes) -> object:
    return json.loads(obj.decode('utf-8'))

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


def pipe_sock(sock: socket.socket) -> Tuple[Callable[[object], None], Callable[[int], object]]:
    """
    Permet d'échanger des objets entre noeuds au travers d'une prise.

    :param sock: Prise connectée à un noeud.
    :return: Fonctions pour envoyer et recevoir un objet Python sérialisable en JSON.
    """
    send = lambda obj: sock.send(json_encode(obj))
    recv = lambda bufsize=1024: json_decode(sock.recv(bufsize))
    return send, recv

def send(host: str, port: int, obj: object, ignore_errors=True) -> None:
    """
    Permet d'envoyer un objet à un noeud au travers d'une prise temporaire.

    :param host: Adresse du noeud.
    :param port: Port associé à cette adresse.
    :param obj: Objet Python sérialisable en JSON.
    :param ignore_errors: Si True les erreurs sont ignorées
    sinon elles sont remontées.
    """
    try:
        sock = create_sock(host, port)
        sock.send(json_encode(obj))
        sock.close()
    except Exception as error:
        if ignore_errors:
            return
        else:
            raise error

def recv(sock: socket.socket, bufsize: int = 2048) -> object:
    """
    Permet de recevoir un objet envoyé par un noeud.
    L'objet envoyé doit être un JSON sérialisé.

    :param sock: Prise connectée à un noeud.
    :param bufsize: Nombre d'octets attendus.
    :return: Objet Python.
    """
    return json_decode(sock.recv(bufsize))

def sha256(obj: object) -> str:
    """
    Fonction de hachage SHA256 d'un objet Python.

    :param obj: Objet Python sérialisable en JSON.
    :return: String du hash de l'objet.
    """
    return hashlib.sha256(json_encode(obj)).hexdigest()

def logging(msg: Union[str, object]) -> None:
    """
    Affichage dans la sortie standard d'un message précédé par sa date d'émission.

    :param msg: Message à afficher.
    """
    print(f"[{dt.datetime.now().strftime('%Y-%d-%m %H:%M:%S')}] {msg}")
