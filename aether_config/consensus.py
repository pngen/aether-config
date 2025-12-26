# aether_config/consensus.py
"""
Lightweight consensus protocol implementation.
"""

import asyncio
import time
from enum import Enum
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from .core import ConfigSchema

class NodeRole(Enum):
    """Consensus node roles."""
    LEADER = "leader"
    FOLLOWER = "follower"
    CANDIDATE = "candidate"

@dataclass
class RaftMessage:
    """Raft-style message structure."""
    term: int
    message_type: str
    sender_id: str
    data: Optional[Dict] = None

class ConsensusNode:
    """Simplified consensus node for configuration coordination."""
    
    def __init__(self, node_id: str, peers: List[str], storage_backend):
        self.node_id = node_id
        self.peers = set(peers)
        self.storage = storage_backend
        self.role = NodeRole.FOLLOWER
        self.current_term = 0
        self.voted_for = None
        self.leader_id = None
        self.commit_index = 0
        self.last_applied = 0
        self.election_timeout = 1.0  # seconds
        self.heartbeat_interval = 0.5  # seconds
        self.last_heartbeat = time.time()
        self.vote_lock = asyncio.Lock()
        self.state_lock = asyncio.Lock()
        
    async def start(self):
        """Start the consensus node."""
        if self.role == NodeRole.FOLLOWER:
            await self._start_election_timer()
    
    async def _start_election_timer(self):
        """Start election timer for follower nodes."""
        while True:
            await asyncio.sleep(self.election_timeout)
            if self.role == NodeRole.FOLLOWER:
                await self._trigger_election()
    
    async def _trigger_election(self):
        """Trigger a new election."""
        async with self.state_lock:
            self.current_term += 1
            self.role = NodeRole.CANDIDATE
            self.voted_for = self.node_id
            
        # Request votes from peers
        vote_requests = []
        for peer in self.peers:
            vote_requests.append(self._request_vote(peer))
        
        results = await asyncio.gather(*vote_requests, return_exceptions=True)
        votes_received = sum(1 for r in results if isinstance(r, bool) and r)
        
        # If majority voted yes
        if votes_received > len(self.peers) // 2:
            async with self.state_lock:
                self.role = NodeRole.LEADER
                self.leader_id = self.node_id
                await self._start_heartbeat()
    
    async def _request_vote(self, peer: str) -> bool:
        """Request vote from a peer."""
        # Simplified - in real implementation would make HTTP request
        return True  # Simulate successful vote
    
    async def _start_heartbeat(self):
        """Start sending heartbeats to followers."""
        while self.role == NodeRole.LEADER:
            await asyncio.sleep(self.heartbeat_interval)
            await self._send_heartbeat()
    
    async def _send_heartbeat(self):
        """Send heartbeat to followers."""
        # Simplified - in real implementation would make HTTP request
        pass
    
    async def propose_config(self, config: ConfigSchema) -> bool:
        """Propose a new configuration version."""
        if self.role != NodeRole.LEADER:
            return False
            
        try:
            # In a real implementation, this would replicate to followers
            await self.storage.save_config(config)
            return True
        except Exception:
            return False
    
    async def apply_config(self, config: ConfigSchema) -> bool:
        """Apply configuration to local storage."""
        try:
            await self.storage.save_config(config)
            return True
        except Exception:
            return False