from mini_btc import Wallet
import argparse


help = \
"""
* help: Affiche la liste des commandes disponibles.

* update_balance: Met à jour les UTXO du porte-feuille.

* get_balance: Affiche le solde du porte-feuille.
Note: Mettre à jour les UTXO au préalable.

* transfer <pubkey> <value>: Transfère la somme <value> à <pubkey>.
Note: Mettre à jour les UTXO avant et après le transfert.

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

    elif "get_balance" == cmd[0]:
        print(f"{wallet.get_balance()} BTC")

    elif "update_balance" == cmd[0]:
        print("SYNC")
        wallet.update_balance()

    elif "transfer" == cmd[0] and (len(cmd) == 1 or len(cmd) == 3):
        # Transaction vide
        if len(cmd) == 1:
            success = wallet.empty_transfer()
        # Transaction classique
        else:
            success = wallet.transfer(dest_pubkey=cmd[1], value=int(cmd[2]))

        if success:
            print("SUCCESS")
        else:
            print("FAILURE")

    elif "exit" == cmd[0]:
        wallet.shutdown(); break

    # Commande invalide
    else:
        print("ERROR")
