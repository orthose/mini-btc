import socket, json, sys
import datetime as dt
from base58 import b58encode, b58decode
from binascii import hexlify, unhexlify
from Crypto.PublicKey import DSA
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
from typing import Callable, Tuple, Union


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
    return SHA256.new(json_encode(obj)).hexdigest()


def dsa_generate(size=1024) -> DSA.DsaKey:
    """
    Génère une clé privée DSA aléatoire.

    :param size: Taille de la clé.
    :return: Clé privée secrète.
    """
    private_key = DSA.generate(size)
    return private_key


def dsa_export(private_key: DSA.DsaKey, key_file: str):
    """
    Exporte une clé privée dans un fichier binaire.

    :param private_key: Clé privée secrète.
    :param key_file: Chemin du fichier de sortie.
    """
    with open(key_file, 'wb') as f:
        f.write(private_key.export_key("DER"))


def dsa_import(key_file: str) -> DSA.DsaKey:
    """
    Importe une clé privée depuis un fichier binaire.

    :param key_file: Chemin du fichier binaire.
    :return: Clé privée secrète.
    """
    with open(key_file, 'rb') as f:
        return DSA.import_key(f.read())


def dsa_publickey(private_key: DSA.DsaKey) -> Tuple[str, str]:
    """
    Permet d'obtenir la clé publique et l'adresse à partir de la clé privée.
    Elles sont encodées en base 58.

    :param private_key: Clé privée secrète.
    :return: Le couple clé publique, adresse.
    """
    public_key = private_key.publickey().export_key("DER")
    address = b58encode(SHA256.new(public_key).digest()).decode('utf-8')
    public_key = b58encode(public_key).decode('utf-8')
    return public_key, address


def dsa_sign(private_key: DSA.DsaKey, data: object) -> str:
    """
    Permet de signer une transaction en cryptant son hash avec la clé privée.

    :param private_key: Clé privée secrète.
    :param data: Données à hacher.
    :return: Chaîne encryptée du hash.
    """
    hash = SHA256.new(json_encode(data))
    return hexlify(DSS.new(private_key, 'fips-186-3').sign(hash)).decode("utf-8")


def dsa_verify(public_key: str, sign: str, data: object) -> bool:
    """
    Vérifie la signature selon la clé publique.

    :param public_key: Clé publique pour décrypter la signature.
    :param sign: Signature à vérifier.
    :param data: Données à hacher.
    :return: True si la signature correspond au hash False sinon.
    """
    try:
        public_key = DSA.import_key(b58decode(public_key.encode("utf-8")))
        hash = SHA256.new(json_encode(data))
        DSS.new(public_key, 'fips-186-3').verify(hash, unhexlify(sign))
        return True
    except:
        return False


def logging(msg: Union[str, object]) -> None:
    """
    Affichage dans la sortie standard d'un message précédé par sa date d'émission.

    :param msg: Message à afficher.
    """
    print(f"[{dt.datetime.now().strftime('%Y-%d-%m %H:%M:%S')}] {msg}")
