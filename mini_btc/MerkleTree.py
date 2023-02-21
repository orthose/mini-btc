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

        :param hashs: Liste de hashs sous forme de string.
        Si None ou liste vide crée un arbre vide.
        On suppose que les hashs sont uniques.
        """
        self.hashs = [] if hashs is None else hashs

        if len(self.hashs) == 0:
            self.tree = None
            return

        # Niveau 0 des feuilles
        lvl = 0
        tree = [MerkleNode(h, lvl, None, None) for h in self.hashs]

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

    def get_root(self) -> str:
        """
        Renvoie le hash de la racine de l'arbre de Merkle.

        :return: String du hash correspondant.
        """
        return self.tree.hash

    def get_proof(self, hash: str) -> List[str]:
        """
        Construit la preuve qu'un hash est dans l'arbre de Merkle
        sous forme d'une liste de hashs.

        :param hash: String du hash à prouver.
        :return: Liste de string des hashs constituant la preuve.
        Liste vide si un seul hash dans l'arbre (à la racine).
        """
        # Indice du hash à prouver dans la liste des hashs
        index = self.hashs.index(hash)

        def build_proof(index: int, tree: 'MerkleNode', proof: List[str]) -> List[str]:
            # On atteint le niveau des feuilles
            if tree.level == 0:
                return proof
            # La feuille recherchée est à gauche
            elif index < 2**(tree.level-1):
                proof.append(tree.right.hash)
                return build_proof(index, tree.left, proof)
            # La feuille recherchée est à droite
            else:
                proof.append(tree.left.hash)
                # On rescale l'index à partir de 0 pour le sous-arbre droit
                return build_proof(index-2**(tree.level-1), tree.right, proof)

        return build_proof(index, self.tree, [])

    @staticmethod
    def verify_proof(hash: str, root: str, proof: List[str]) -> bool:
        """
        Vérifie la preuve d'un hash par rapport à la racine d'un arbre de Merkle.

        :param hash: String du hash à prouver.
        :param root: String du hash de la racine de l'arbre.
        :param proof: Liste de string des hashs prouvant le hash.
        :return: True si preuve valide False sinon.
        """
        proof = proof.copy()

        for _ in range(len(proof)):
            hash = sum_hash(hash, proof.pop())

        return root == hash
