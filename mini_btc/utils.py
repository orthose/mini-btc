import socket, json, hashlib, sys
from base58 import b58encode
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


def send(host: str, port: int, obj: object, ignore_errors=True) -> None:
    """
    Permet d'envoyer un objet à un noeud au travers d'une prise temporaire.
    La fonction implémente un protocole permettant au destinataire de savoir
    quelle taille de paquet il attend.

    :param host: Adresse du noeud.
    :param port: Port associé à cette adresse.
    :param obj: Objet Python sérialisable en JSON.
    :param ignore_errors: Si True les erreurs sont ignorées.
    """
    try:
        # Création de la prise
        sock = create_sock(host, port)
        # Détermination de la taille du paquet
        obj = json_encode(obj)
        length = sys.getsizeof(obj)
        # Envoi de la taille du paquet
        sock.sendall(json_encode({"Packet-Length": length}))
        # Synchronisation avec le destinataire
        assert length == json_decode(sock.recv(128))["Packet-Length"]
        # Envoi du paquet complet
        sock.sendall(obj)
        # Fermeture de la prise
        sock.close()

    except Exception as error:
        if ignore_errors:
            return
        else:
            raise error


def recv(sock: socket.socket, ignore_errors=True) -> object:
    """
    Permet de recevoir un objet envoyé par un noeud.
    L'objet envoyé doit être un JSON sérialisé.
    La fonction suit le protocole de la fonction précédente.

    :param sock: Prise connectée à un noeud.
    :param ignore_errors: Si True les erreurs sont ignorées.
    :return: Objet Python.
    """
    try:
        # Réception de la taille du paquet
        obj = json_decode(sock.recv(128))
        bufsize = obj["Packet-Length"]
        # Synchronisation avec l'expéditeur
        sock.sendall(json_encode(obj))
        # Réception du paquet
        return json_decode(sock.recv(bufsize))

    except Exception as error:
        if ignore_errors:
            return
        else:
            raise error


def sha256(obj: object) -> str:
    """
    Fonction de hachage SHA256 d'un objet Python.

    :param obj: Objet Python sérialisable en JSON.
    :return: String du hash de l'objet.
    """
    return hashlib.sha256(json_encode(obj)).hexdigest()


def rsa_publickey(private_key: object) -> Tuple[str, str]:
    """
    Permet d'obtenir la clé publique et l'adresse à partir de la clé privée.
    Elles sont encodées en base 58.

    :param private_key: Clé privée secrète.
    :return: Le couple clé publique, adresse.
    """
    public_key = private_key.publickey().exportKey("DER")
    address = b58encode(hashlib.sha256(public_key).digest()).decode('utf-8')
    public_key = b58encode(public_key).decode('utf-8')
    return public_key, address


def logging(msg: Union[str, object]) -> None:
    """
    Affichage dans la sortie standard d'un message précédé par sa date d'émission.

    :param msg: Message à afficher.
    """
    print(f"[{dt.datetime.now().strftime('%Y-%d-%m %H:%M:%S')}] {msg}")
