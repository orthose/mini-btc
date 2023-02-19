from mini_btc.utils import sum_hash
from mini_btc import Transaction
from mini_btc import MerkleTree


hashs = None
mt = MerkleTree(hashs)
assert mt.tree is None

hashs = []
mt = MerkleTree(hashs)
assert mt.tree is None

# Hash de transactions vides
hashs = [Transaction().to_dict()["hash"] for _ in range(1)]
mt = MerkleTree(hashs)
assert 0 == mt.tree.level
assert hashs[0] == mt.tree.hash
assert mt.tree.is_leaf()

hashs = [Transaction().to_dict()["hash"] for _ in range(2)]
mt = MerkleTree(hashs)
assert 1 == mt.tree.level
assert sum_hash(hashs[0], hashs[1]) == mt.tree.hash
assert 0 == mt.tree.left.level
assert hashs[0] == mt.tree.left.hash
assert mt.tree.left.is_leaf()
assert 0 == mt.tree.right.level
assert hashs[1] == mt.tree.right.hash
assert mt.tree.right.is_leaf()

hashs = [Transaction().to_dict()["hash"] for _ in range(3)]
mt = MerkleTree(hashs)
assert 2 == mt.tree.level
assert sum_hash(mt.tree.left.hash, mt.tree.right.hash) == mt.tree.hash
assert 1 == mt.tree.left.level
assert sum_hash(mt.tree.left.left.hash, mt.tree.left.right.hash) == mt.tree.left.hash
assert 0 == mt.tree.left.left.level and mt.tree.left.left.is_leaf()
assert hashs[0] == mt.tree.left.left.hash
assert 0 == mt.tree.left.right.level and mt.tree.left.right.is_leaf()
assert hashs[1] == mt.tree.left.right.hash
assert 0 == mt.tree.right.level and mt.tree.right.is_leaf()
assert hashs[2] == mt.tree.right.hash
