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
assert hashs[0] == mt.get_root()
assert mt.tree.is_leaf()
proof = mt.get_proof(hashs[0])
assert 1 == len(proof)
assert proof[0] == hashs[0]

hashs = [Transaction().to_dict()["hash"] for _ in range(2)]
mt = MerkleTree(hashs)
assert 1 == mt.tree.level
assert sum_hash(hashs[0], hashs[1]) == mt.get_root()
assert 0 == mt.tree.left.level
assert hashs[0] == mt.tree.left.hash
assert mt.tree.left.is_leaf()
assert 0 == mt.tree.right.level
assert hashs[1] == mt.tree.right.hash
assert mt.tree.right.is_leaf()
proof = mt.get_proof(hashs[0])
assert 1 == len(proof)
assert hashs[1] == proof[0]
proof = mt.get_proof(hashs[1])
assert 1 == len(proof)
assert hashs[0] == proof[0]

hashs = [Transaction().to_dict()["hash"] for _ in range(3)]
mt = MerkleTree(hashs)
assert 2 == mt.tree.level
assert sum_hash(mt.tree.left.hash, mt.tree.right.hash) == mt.get_root()
assert 1 == mt.tree.left.level
assert sum_hash(mt.tree.left.left.hash, mt.tree.left.right.hash) == mt.tree.left.hash
assert 0 == mt.tree.left.left.level and mt.tree.left.left.is_leaf()
assert hashs[0] == mt.tree.left.left.hash
assert 0 == mt.tree.left.right.level and mt.tree.left.right.is_leaf()
assert hashs[1] == mt.tree.left.right.hash
assert 0 == mt.tree.right.level and mt.tree.right.is_leaf()
assert hashs[2] == mt.tree.right.hash
proof = mt.get_proof(hashs[0])
assert 2 == len(proof)
assert proof[0] == mt.tree.right.hash
assert proof[1] == mt.tree.left.right.hash
proof = mt.get_proof(hashs[1])
assert 2 == len(proof)
assert proof[0] == mt.tree.right.hash
assert proof[1] == mt.tree.left.left.hash
proof = mt.get_proof(hashs[2])
assert 1 == len(proof)
assert proof[0] == mt.tree.left.hash

hashs = [Transaction().to_dict()["hash"] for _ in range(6)]
mt = MerkleTree(hashs)
proof = mt.get_proof(hashs[0])
assert 3 == len(proof)
assert proof[0] == mt.tree.right.hash
assert proof[1] == mt.tree.left.right.hash
assert proof[2] == mt.tree.left.left.right.hash
proof = mt.get_proof(hashs[1])
assert 3 == len(proof)
assert proof[0] == mt.tree.right.hash
assert proof[1] == mt.tree.left.right.hash
assert proof[2] == mt.tree.left.left.left.hash
proof = mt.get_proof(hashs[2])
assert 3 == len(proof)
assert proof[0] == mt.tree.right.hash
assert proof[1] == mt.tree.left.left.hash
assert proof[2] == mt.tree.left.right.right.hash
proof = mt.get_proof(hashs[3])
assert 3 == len(proof)
assert proof[0] == mt.tree.right.hash
assert proof[1] == mt.tree.left.left.hash
assert proof[2] == mt.tree.left.right.left.hash
proof = mt.get_proof(hashs[4])
assert 2 == len(proof)
assert proof[0] == mt.tree.left.hash
assert proof[1] == mt.tree.right.right.hash
proof = mt.get_proof(hashs[5])
assert 2 == len(proof)
assert proof[0] == mt.tree.left.hash
assert proof[1] == mt.tree.right.left.hash
