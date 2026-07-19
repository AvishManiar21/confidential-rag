"""Midnight blockchain service for contract interaction."""

from typing import Optional, Dict, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class MidnightService:
    """Service for interacting with Midnight blockchain contracts."""

    def __init__(self):
        """Initialize Midnight service."""
        self.node_url = settings.midnight_node_url
        self.indexer_url = settings.midnight_indexer_url
        self.proof_server_url = settings.midnight_proof_server_url
        self.contract_address = settings.midnight_contract_address
        self.private_key = settings.midnight_private_key
        logger.info(f"Initialized Midnight service")
        logger.info(f"  Node: {self.node_url}")
        logger.info(f"  Indexer: {self.indexer_url}")
        logger.info(f"  Proof Server: {self.proof_server_url}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def submit_commitment(
        self,
        commitment_hash: str,
        merkle_root: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Submit a commitment to the Midnight contract.

        Args:
            commitment_hash: Document commitment hash
            merkle_root: Merkle tree root hash
            metadata: Optional metadata

        Returns:
            Dict: Transaction result with tx_hash and block_number
        """
        try:
            # Placeholder implementation for Midnight contract interaction
            # In production, this would use the Midnight SDK

            logger.info(f"Submitting commitment to Midnight: {commitment_hash}")

            # Simulate contract call
            payload = {
                "method": "submit_commitment",
                "params": {
                    "commitment": commitment_hash,
                    "merkle_root": merkle_root,
                    "metadata": metadata or {}
                },
                "contract_address": self.contract_address
            }

            # TODO: Replace with actual Midnight SDK call
            # For now, return mock response
            result = {
                "success": True,
                "tx_hash": f"0x{commitment_hash[:64]}",
                "block_number": 12345,
                "gas_used": 21000,
                "timestamp": None
            }

            logger.info(f"Commitment submitted successfully: {result['tx_hash']}")
            return result

        except Exception as e:
            logger.error(f"Error submitting commitment to Midnight: {str(e)}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def verify_proof(
        self,
        proof_data: Dict[str, Any],
        merkle_root: str
    ) -> Dict[str, Any]:
        """
        Verify a ZK proof on-chain.

        Args:
            proof_data: Proof data to verify
            merkle_root: Expected Merkle root

        Returns:
            Dict: Verification result
        """
        try:
            logger.info("Verifying proof on Midnight")

            # Placeholder implementation
            payload = {
                "method": "verify_proof",
                "params": {
                    "proof": proof_data,
                    "merkle_root": merkle_root
                },
                "contract_address": self.contract_address
            }

            # TODO: Replace with actual Midnight SDK call
            result = {
                "verified": True,
                "tx_hash": f"0x{merkle_root[:64]}",
                "block_number": 12346,
                "gas_used": 45000
            }

            logger.info(f"Proof verification result: {result['verified']}")
            return result

        except Exception as e:
            logger.error(f"Error verifying proof on Midnight: {str(e)}")
            raise

    async def get_commitment(self, commitment_hash: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a commitment from the blockchain.

        Args:
            commitment_hash: Commitment to retrieve

        Returns:
            Dict: Commitment data or None if not found
        """
        try:
            logger.info(f"Retrieving commitment: {commitment_hash}")

            # Placeholder implementation
            # TODO: Replace with actual Midnight SDK call
            result = {
                "commitment": commitment_hash,
                "merkle_root": "mock_root",
                "block_number": 12345,
                "timestamp": None,
                "metadata": {}
            }

            return result

        except Exception as e:
            logger.error(f"Error retrieving commitment: {str(e)}")
            return None

    async def get_merkle_root(self, document_id: int) -> Optional[str]:
        """
        Get Merkle root for a document from the blockchain.

        Args:
            document_id: Document ID

        Returns:
            str: Merkle root hash or None
        """
        try:
            logger.info(f"Retrieving Merkle root for document {document_id}")

            # Placeholder implementation
            # TODO: Replace with actual Midnight SDK call
            return "mock_merkle_root"

        except Exception as e:
            logger.error(f"Error retrieving Merkle root: {str(e)}")
            return None

    async def check_connection(self) -> Dict[str, bool]:
        """
        Check connection to Midnight services.

        Returns:
            Dict: Status of each service (node, indexer, proof_server)
        """
        status = {
            "node": False,
            "indexer": False,
            "proof_server": False
        }

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Check Midnight Node
                try:
                    response = await client.get(f"{self.node_url}/health")
                    status["node"] = response.status_code == 200
                    logger.info(f"Midnight Node: {'✓ Connected' if status['node'] else '✗ Unreachable'}")
                except Exception as e:
                    logger.warning(f"Cannot connect to Midnight Node: {str(e)}")

                # Check Indexer
                try:
                    response = await client.get(f"{self.indexer_url}/health")
                    status["indexer"] = response.status_code == 200
                    logger.info(f"Midnight Indexer: {'✓ Connected' if status['indexer'] else '✗ Unreachable'}")
                except Exception as e:
                    logger.warning(f"Cannot connect to Midnight Indexer: {str(e)}")

                # Check Proof Server
                try:
                    response = await client.get(f"{self.proof_server_url}/health")
                    status["proof_server"] = response.status_code == 200
                    logger.info(f"Proof Server: {'✓ Connected' if status['proof_server'] else '✗ Unreachable'}")
                except Exception as e:
                    logger.warning(f"Cannot connect to Proof Server: {str(e)}")

        except Exception as e:
            logger.error(f"Error checking Midnight connections: {str(e)}")

        return status


# Global instance
midnight_service = MidnightService()
