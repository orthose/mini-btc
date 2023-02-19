from mini_btc.utils import sum_hash
from typing import Optional, List


class MerkleNode:
    def __init__(self, hash: str, level: int,
                 left: Optional['MerkleNode'] = None,
                 right: Optional['MerkleNode'] = None):
        """
        Création d'un noeud de l'arbre de Merkle.
        Si right=None et left=None alors c'est une feuille.

        :param hash: Valeur du hash portée par le noeud.
        :param level: Niveau du noeud dans l'arbre
        0 pour les feuilles et n pour la racine.
        :param right: Sous-arbre gauche.
        :param left: Sous-arbre droit.
        """
        assert str == type(hash)
        assert int == type(level) and 0 <= level
        self.hash = hash
        self.level = level
        self.left = left
        self.right = right

    def is_leaf(self):
        """
        Le noeud est-il est une feuille ?

        :return: True si c'est une feuille False sinon.
        """
        return self.right is None and self.left is None

class MerkleTree:
    def __init__(self, hashs: Optional[List[str]] = None):
        """
        Initialise un arbre de Merkle à partir d'une liste de hashs.

        :param hashs: Liste de hashs sous forme de chaînes de caractères.
        Si None ou liste vide crée un arbre vide.
        """
        if hashs is None or len(hashs) == 0:
            self.tree = None
            return

        # Niveau 0 des feuilles
        lvl = 0
        tree = [MerkleNode(h, lvl, None, None) for h in hashs]

        # Fusion des arbres par étage
        while len(tree) > 1:
            lvl += 1
            new_tree = []
            for i in range(0, len(tree), 2):
                # Dernier arbre impair
                if i+1 == len(tree):
                    new_tree.append(tree[i])
                # Fusion de 2 arbres
                else:
                    h = sum_hash(tree[i].hash, tree[i+1].hash)
                    new_tree.append(MerkleNode(h, lvl, tree[i], tree[i+1]))
            tree = new_tree

        self.tree = tree[0]
