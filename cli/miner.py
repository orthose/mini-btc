from mini_btc import Miner
import argparse


parser = argparse.ArgumentParser(
    description="Daemon de minage de Mini BTC.")

parser.add_argument("-p", "--pubkey", dest="pubkey", type=str,
    required=True, help="Clé publique pour la récompense de minage requis.")

parser.add_argument("-lh", "--listen-host", dest="listen_host", type=str,
    default="localhost", help="Adresse d'écoute par défaut localhost.")

parser.add_argument("-lp", "--listen-port", dest="listen_port", type=int,
    default=8001, help="Port d'écoute par défaut 8001.")

parser.add_argument("-rh", "--remote-host", dest="remote_host", type=str,
    default="localhost", help="Adresse du noeud auquel se connecter par défaut localhost.")

parser.add_argument("-rp", "--remote-port", dest="remote_port", type=int,
    help="Port d'écoute du noeud auquel se connecter. Ne pas préciser si premier noeud du réseau.")

parser.add_argument("-n", "--max-nodes", dest="max_nodes", type=int,
    default=10, help="Nombre maximum de noeuds voisins actifs à conserver par défaut 10.")

# Note: Tous les noeuds du réseau doivent avoir le même block_size et la même difficulty.
parser.add_argument("-bs", "--block-size", dest="block_size", type=int,
    default=3, help="Nombre de transactions d'un bloc par défaut 3")

parser.add_argument("-d", "--difficulty", dest="difficulty", type=int,
    default=5, help="Difficulté du minage par défaut 5.")

args = parser.parse_args()
print(args)

miner = Miner(args.pubkey, args.listen_host, args.listen_port,
              args.remote_host, args.remote_port,
              args.max_nodes, args.block_size, args.difficulty)
miner.start()
