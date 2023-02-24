from mini_btc import Wallet
import argparse


help = \
"""
* help: Affiche la liste des commandes disponibles.

* update_balance: Met à jour les UTXO du porte-feuille.

* get_balance: Affiche le solde du porte-feuille.
Note: Mettre à jour les UTXO au préalable.

* register <name> <pubkey>: Enregistrement d'une clé publique dans l'annuaire.
Si aucun argument renseigné affiche l'annuaire.

* transfer <pubkey> <value>: Transfère la somme <value> à <pubkey>.
La <pubkey> peut être une entrée de l'annuaire ou une clé publique complète.
Note: Mettre à jour les UTXO avant et après le transfert.

* sync_block: Met à jour la blockchain du porte-feuille.

* block_count: Donne le nombre de blocs connus par le porte-feuille.

* get_proof <txid>: Demande la preuve d'une transaction.
Si <txid> n'est pas renseigné renvoie la liste des preuves reçues.

* verify_proof <txid>: Vérifie la preuve d'une transaction.
Si <txid> n'est pas renseigné vérifie toutes les preuves reçues.
Note: Mettre à jour la blockchain et demander la preuve au préalable.

* exit: Quitte le porte-feuille.
"""

parser = argparse.ArgumentParser(
    description="Porte-feuille Mini BTC en ligne de commandes.")

parser.add_argument("-w", "--wallet-file", dest="wallet_file", type=str,
    help="Chemin du fichier binaire contenant la clé privée du porte-feuille.")

parser.add_argument("-lh", "--listen-host", dest="listen_host", type=str,
    default="localhost", help="Adresse d'écoute du porte-feuille par défaut localhost.")

parser.add_argument("-lp", "--listen-port", dest="listen_port", type=int,
    default=8000, help="Port d'écoute du porte-feuille par défaut 8000.")

parser.add_argument("-rh", "--remote-host", dest="remote_host", type=str,
    default="localhost", help="Adresse du noeud auquel se connecter par défaut localhost.")

parser.add_argument("-rp", "--remote-port", dest="remote_port", type=int,
    required=True, help="Port d'écoute du noeud auquel se connecter requis.")

parser.add_argument("-v", "--verbose", dest="verbose", type=int, default=0,
    help="Niveau de verbosité entre 0 et 2.")

args = parser.parse_args()

print(args, end="\n\n")

wallet_file = args.wallet_file

if wallet_file is None:
    qst = "Avez-vous déjà un porte-feuille (Y/n) ? "
    while (rsp := input(qst).lower()) not in ['', 'y', 'n']: continue

    wallet_file = input("Nom de fichier: ")

    # Création d'un porte-feuille
    if rsp == 'n':
        Wallet.create(wallet_file)

# Chargement du porte-feuille
wallet = Wallet(wallet_file, args.listen_host, args.listen_port,
                args.remote_host, args.remote_port, args.verbose)
wallet.start()

print("\nBienvenue sur le porte-feuille Mini BTC.")
print("Tapez help pour voir la liste des commandes.\n")

# Exécution des commandes
while True:
    cmd = input('> ').split()

    # Saut de ligne
    if len(cmd) == 0: continue

    elif "help" == cmd[0] and len(cmd) == 1:
        print(help)

    elif "get_balance" == cmd[0] and len(cmd) == 1:
        print(f"{wallet.get_balance()} BTC")

    elif "update_balance" == cmd[0] and len(cmd) == 1:
        print("SYNC")
        wallet.update_balance()

    elif "register" == cmd[0] and (len(cmd) == 1 or len(cmd) == 3):
        if len(cmd) == 1:
            for name in wallet.addr:
                print(f"{name} = {wallet.addr[name][0:64]}")
        else:
            print(f"{cmd[1]} = {cmd[2][0:64]}")
            wallet.register(cmd[1], cmd[2])

    elif "transfer" == cmd[0] and (len(cmd) == 1 or len(cmd) == 3):
        # Transaction vide
        if len(cmd) == 1:
            txid = wallet.empty_transfer()
        # Transaction classique
        else:
            txid = wallet.transfer(dest_pubkey=cmd[1], value=int(cmd[2]))

        if txid is not None:
            print(f"TXID: {txid}")
        else:
            print("FAILURE")

    elif "sync_block" == cmd[0] and len(cmd) == 1:
        print("SYNC")
        wallet.sync_block()

    elif "block_count" == cmd[0] and len(cmd) == 1:
        print(len(wallet.ledger))

    elif "get_proof" == cmd[0] and len(cmd) <= 2:
        if len(cmd) == 1:
            for txid in wallet.proof_tx: print(txid)
        else:
            print("SYNC")
            wallet.get_proof(cmd[1])

    elif "verify_proof" == cmd[0] and len(cmd) <= 2:
        for txid in ([cmd[1]] if len(cmd) == 2 else wallet.proof_tx):
            if wallet.verify_proof(txid):
                print(f"SUCCESS {txid}")
            else:
                print(f"FAILURE {txid}")

    elif "exit" == cmd[0] and len(cmd) == 1:
        wallet.shutdown(); break

    # Commande invalide
    else:
        print("ERROR")
