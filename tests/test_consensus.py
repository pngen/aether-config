# tests/test_consensus.py
"""
Unit tests for consensus implementation.
"""

import pytest
from aether_config.consensus import ConsensusNode, NodeRole
from aether_config.storage import InMemoryStorage

@pytest.fixture
def storage():
    return InMemoryStorage()

@pytest.fixture
def consensus_node(storage):
    return ConsensusNode("node1", ["node2", "node3"], storage)

@pytest.mark.asyncio
async def test_consensus_initialization(consensus_node):
    """Test consensus node initialization."""
    assert consensus_node.node_id == "node1"
    assert consensus_node.role == NodeRole.FOLLOWER
    assert consensus_node.current_term == 0

@pytest.mark.asyncio
async def test_propose_config(consensus_node):
    """Test proposing a configuration."""
    schema = {
        "name": "test-config",
        "version": 1,
        "data": {"key": "value"}
    }
    
    # Should fail when not leader
    result = await consensus_node.propose_config(schema)
    assert result is False