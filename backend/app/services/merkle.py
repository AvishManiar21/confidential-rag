"""Merkle tree service for generating and verifying Merkle proofs."""

from typing import List, Dict, Any, Optional, Tuple
import hashlib
from dataclasses import dataclass

from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class MerkleNode:
    """Merkle tree node."""
    hash: str
    left: Optional['MerkleNode'] = None
    right: Optional['MerkleNode'] = None


@dataclass
class MerkleProof:
    """Merkle proof data structure."""
    leaf_hash: str
    proof_hashes: List[str]
    proof_positions: List[str]  # 'left' or 'right'
    root_hash: str


class MerkleTree:
    """Merkle tree implementation for document commitments."""

    def __init__(self, leaves: List[str]):
        """
        Initialize Merkle tree from leaf hashes.

        Args:
            leaves: List of leaf hashes (commitments)
        """
        if not leaves:
            raise ValueError("Cannot create Merkle tree with empty leaves")

        self.leaves = leaves
        self.root = self._build_tree(leaves)
        logger.info(f"Built Merkle tree with {len(leaves)} leaves, root: {self.root.hash}")

    @staticmethod
    def _hash_pair(left: str, right: str) -> str:
        """
        Hash a pair of nodes.

        Args:
            left: Left node hash
            right: Right node hash

        Returns:
            str: Combined hash
        """
        combined = left + right
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()

    def _build_tree(self, hashes: List[str]) -> MerkleNode:
        """
        Recursively build Merkle tree.

        Args:
            hashes: List of hashes at current level

        Returns:
            MerkleNode: Root node of (sub)tree
        """
        if len(hashes) == 1:
            return MerkleNode(hash=hashes[0])

        # If odd number of hashes, duplicate the last one
        if len(hashes) % 2 == 1:
            hashes = hashes + [hashes[-1]]

        # Build parent level
        parent_hashes = []
        nodes = []

        for i in range(0, len(hashes), 2):
            left_hash = hashes[i]
            right_hash = hashes[i + 1]

            left_node = MerkleNode(hash=left_hash)
            right_node = MerkleNode(hash=right_hash)

            parent_hash = self._hash_pair(left_hash, right_hash)
            parent_node = MerkleNode(hash=parent_hash, left=left_node, right=right_node)

            parent_hashes.append(parent_hash)
            nodes.append(parent_node)

        # Recursively build upper levels
        if len(parent_hashes) == 1:
            return nodes[0]
        else:
            return self._build_tree(parent_hashes)

    def get_root(self) -> str:
        """
        Get Merkle root hash.

        Returns:
            str: Root hash
        """
        return self.root.hash

    def generate_proof(self, leaf_hash: str) -> Optional[MerkleProof]:
        """
        Generate Merkle proof for a specific leaf.

        Args:
            leaf_hash: Hash of the leaf to prove

        Returns:
            MerkleProof: Proof data or None if leaf not found
        """
        try:
            # Find leaf index
            if leaf_hash not in self.leaves:
                logger.warning(f"Leaf hash not found in tree: {leaf_hash}")
                return None

            leaf_index = self.leaves.index(leaf_hash)
            proof_hashes = []
            proof_positions = []

            # Work with a copy of leaves
            current_level = self.leaves.copy()
            current_index = leaf_index

            # Build proof by traversing up the tree
            while len(current_level) > 1:
                # Handle odd number of elements
                if len(current_level) % 2 == 1:
                    current_level.append(current_level[-1])

                # Determine sibling
                if current_index % 2 == 0:
                    # Even index - sibling is on the right
                    sibling_index = current_index + 1
                    proof_positions.append('right')
                else:
                    # Odd index - sibling is on the left
                    sibling_index = current_index - 1
                    proof_positions.append('left')

                proof_hashes.append(current_level[sibling_index])

                # Move to parent level
                next_level = []
                for i in range(0, len(current_level), 2):
                    parent_hash = self._hash_pair(current_level[i], current_level[i + 1])
                    next_level.append(parent_hash)

                current_level = next_level
                current_index = current_index // 2

            return MerkleProof(
                leaf_hash=leaf_hash,
                proof_hashes=proof_hashes,
                proof_positions=proof_positions,
                root_hash=self.root.hash
            )

        except Exception as e:
            logger.error(f"Error generating Merkle proof: {str(e)}")
            return None

    @staticmethod
    def verify_proof(proof: MerkleProof) -> bool:
        """
        Verify a Merkle proof.

        Args:
            proof: Merkle proof to verify

        Returns:
            bool: True if proof is valid
        """
        try:
            current_hash = proof.leaf_hash

            for sibling_hash, position in zip(proof.proof_hashes, proof.proof_positions):
                if position == 'left':
                    current_hash = MerkleTree._hash_pair(sibling_hash, current_hash)
                else:
                    current_hash = MerkleTree._hash_pair(current_hash, sibling_hash)

            is_valid = current_hash == proof.root_hash
            logger.debug(f"Merkle proof verification: {is_valid}")
            return is_valid

        except Exception as e:
            logger.error(f"Error verifying Merkle proof: {str(e)}")
            return False

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert tree to dictionary representation.

        Returns:
            Dict: Tree data
        """
        return {
            "root": self.root.hash,
            "leaves": self.leaves,
            "num_leaves": len(self.leaves)
        }


class MerkleService:
    """Service for Merkle tree operations."""

    @staticmethod
    async def build_tree(commitments: List[str]) -> MerkleTree:
        """
        Build Merkle tree from commitments.

        Args:
            commitments: List of commitment hashes

        Returns:
            MerkleTree: Constructed Merkle tree
        """
        try:
            tree = MerkleTree(commitments)
            logger.info(f"Built Merkle tree with root: {tree.get_root()}")
            return tree
        except Exception as e:
            logger.error(f"Error building Merkle tree: {str(e)}")
            raise

    @staticmethod
    async def generate_proof(
        tree: MerkleTree,
        commitment: str
    ) -> Optional[Dict[str, Any]]:
        """
        Generate Merkle proof for a commitment.

        Args:
            tree: Merkle tree
            commitment: Commitment hash to prove

        Returns:
            Dict: Proof data or None
        """
        try:
            proof = tree.generate_proof(commitment)
            if proof is None:
                return None

            return {
                "leaf_hash": proof.leaf_hash,
                "proof_hashes": proof.proof_hashes,
                "proof_positions": proof.proof_positions,
                "root_hash": proof.root_hash
            }
        except Exception as e:
            logger.error(f"Error generating proof: {str(e)}")
            return None

    @staticmethod
    async def verify_proof(proof_data: Dict[str, Any]) -> bool:
        """
        Verify a Merkle proof from dictionary.

        Args:
            proof_data: Proof data dictionary

        Returns:
            bool: True if valid
        """
        try:
            proof = MerkleProof(
                leaf_hash=proof_data["leaf_hash"],
                proof_hashes=proof_data["proof_hashes"],
                proof_positions=proof_data["proof_positions"],
                root_hash=proof_data["root_hash"]
            )
            return MerkleTree.verify_proof(proof)
        except Exception as e:
            logger.error(f"Error verifying proof: {str(e)}")
            return False


# Global instance
merkle_service = MerkleService()
