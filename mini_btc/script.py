from mini_btc.utils import dsa_verify
from mini_btc import Transaction


def execute(args: str, script: str, tx: Transaction) -> str:
    """
    Exécution d'un script verrouillant une transaction UTXO.
    Le langage commande une machine à pile.
    * CHECKSIG: Vérifie la signature.

    :param args: Arguments séparés par des espaces.
    :param script: Script à exécuter les instructions sont séparées par des espaces.
    :param tx: Transaction à déverrouiller.
    :return: Sommet de la pile.
    """
    tx = tx.to_dict()
    tx.pop("hash")

    stack = []
    args = args.split()
    for arg in args:
        stack.append(arg)
    script = script.split()

    for token in script:
        if "CHECKSIG" == token:
            pubkey = stack.pop()
            sign = stack.pop()
            if dsa_verify(pubkey, sign, tx):
                stack.append("true")
            else:
                stack.append("false")
        else:
            stack.append(token)

    return stack[-1]
