from .consensus_engine import ConsensusEngine

# Global consensus engine instance
consensus = ConsensusEngine()

__all__ = ["consensus", "ConsensusEngine"]
