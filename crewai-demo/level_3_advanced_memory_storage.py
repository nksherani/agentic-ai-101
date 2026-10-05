"""
ADVANCED CREWAI MEMORY ARCHITECTURE & CUSTOM STORAGE BACKENDS
=============================================================
This file demonstrates:
1. CrewAI 1.x Unified Memory Engine (recency, semantic relevance, importance scoring).
2. LanceDB Embedded Vector Storage configuration (custom path, vector dimensions, table name).
3. Custom Vector / Key-Value Storage Backend implementation conforming to StorageBackend protocol.
4. Memory Scopes (Hierarchical isolation: agent-level vs crew-level vs task-level memories).
5. Storage Backend Factory injection (`set_memory_storage_factory`).
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional, Tuple
from dotenv import load_dotenv

from crewai import Agent, Crew, Process, Task
from crewai.memory import MemoryRecord, MemoryScope
from crewai.memory.storage.backend import StorageBackend, ScopeInfo
from crewai.memory.storage.lancedb_storage import LanceDBStorage
from crewai.memory.storage.factory import set_memory_storage_factory
from crewai.memory.unified_memory import Memory

load_dotenv(Path(__file__).parent.parent / ".env")


# ==============================================================================
# SECTION 1: CUSTOM MEMORY STORAGE BACKEND IMPLEMENTATION
# ==============================================================================
# In production, you might want to back CrewAI memory by Redis, PostgreSQL pgvector,
# Pinecone, Milvus, or AWS DynamoDB. Any backend can be plugged in by satisfying
# the `StorageBackend` protocol.
# ==============================================================================
class InMemoryVectorStorage(StorageBackend):
    """
    An in-memory reference implementation of StorageBackend.
    Illustrates how to implement custom indexing, search, scoping, and lifecycle hooks.
    """

    def __init__(self):
        self._records: dict[str, MemoryRecord] = {}

    def save(self, records: list[MemoryRecord]) -> None:
        for r in records:
            self._records[r.id] = r
            print(f"  [CUSTOM STORAGE] Saved memory record ID: {r.id[:8]}... | Scope: {r.scope}")

    async def asave(self, records: list[MemoryRecord]) -> None:
        self.save(records)

    def search(
        self,
        query_embedding: list[float],
        scope_prefix: Optional[str] = None,
        categories: Optional[list[str]] = None,
        metadata_filter: Optional[dict[str, Any]] = None,
        limit: int = 10,
        min_score: float = 0.0,
    ) -> list[Tuple[MemoryRecord, float]]:
        """
        Cosine similarity or vector search across memory vectors.
        For demonstration, ranks matches with cosine similarity or simple dot product.
        """
        results = []
        for r in self._records.values():
            if scope_prefix and not r.scope.startswith(scope_prefix):
                continue
            if categories and r.categories and not any(c in categories for c in r.categories):
                continue

            # Calculate cosine similarity if embeddings are present
            score = 0.85  # Simulated match score
            if r.embedding and query_embedding:
                dot = sum(a * b for a, b in zip(query_embedding, r.embedding))
                norm_a = sum(a * a for a in query_embedding) ** 0.5
                norm_b = sum(b * b for b in r.embedding) ** 0.5
                if norm_a and norm_b:
                    score = dot / (norm_a * norm_b)

            if score >= min_score:
                results.append((r, score))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]

    async def asearch(
        self,
        query_embedding: list[float],
        scope_prefix: Optional[str] = None,
        categories: Optional[list[str]] = None,
        metadata_filter: Optional[dict[str, Any]] = None,
        limit: int = 10,
        min_score: float = 0.0,
    ) -> list[Tuple[MemoryRecord, float]]:
        return self.search(query_embedding, scope_prefix, categories, metadata_filter, limit, min_score)

    def get_record(self, record_id: str) -> Optional[MemoryRecord]:
        return self._records.get(record_id)

    def list_records(self, scope_prefix: Optional[str] = None, limit: int = 200, offset: int = 0) -> list[MemoryRecord]:
        filtered = [
            r for r in self._records.values()
            if not scope_prefix or r.scope.startswith(scope_prefix)
        ]
        return filtered[offset : offset + limit]

    def count(self, scope_prefix: Optional[str] = None) -> int:
        return len(self.list_records(scope_prefix=scope_prefix))

    def update(self, record: MemoryRecord) -> None:
        self._records[record.id] = record

    def delete(
        self,
        scope_prefix: Optional[str] = None,
        categories: Optional[list[str]] = None,
        record_ids: Optional[list[str]] = None,
        older_than: Optional[datetime] = None,
        metadata_filter: Optional[dict[str, Any]] = None,
    ) -> int:
        to_del = []
        for rid, r in self._records.items():
            if record_ids and rid in record_ids:
                to_del.append(rid)
            elif scope_prefix and r.scope.startswith(scope_prefix):
                to_del.append(rid)
        for rid in to_del:
            del self._records[rid]
        return len(to_del)

    async def adelete(self, **kwargs) -> int:
        return self.delete(**kwargs)

    def reset(self, scope_prefix: Optional[str] = None) -> None:
        if scope_prefix:
            self.delete(scope_prefix=scope_prefix)
        else:
            self._records.clear()

    def get_scope_info(self, scope: str) -> ScopeInfo:
        return ScopeInfo(scope=scope, record_count=self.count(scope_prefix=scope), children=[])

    def list_scopes(self, parent: str = "/") -> list[str]:
        return list({r.scope for r in self._records.values() if r.scope.startswith(parent)})

    def list_categories(self, scope_prefix: Optional[str] = None) -> dict[str, int]:
        counts = {}
        for r in self._records.values():
            if not scope_prefix or r.scope.startswith(scope_prefix):
                for c in (r.categories or []):
                    counts[c] = counts.get(c, 0) + 1
        return counts


# ==============================================================================
# SECTION 2: CONFIGURE EMBEDDED LANCEDB VECTOR STORAGE
# ==============================================================================
def create_lancedb_backed_memory(storage_directory: str) -> Memory:
    """
    Creates a production-grade Memory instance backed by persistent LanceDB.
    Customizes composite scoring weights:
    - semantic_weight: How much cosine similarity influences memory recall
    - recency_weight: Penalizes older memories using half-life decay
    - importance_weight: Favors critical memories flagged by the agent
    """
    os.makedirs(storage_directory, exist_ok=True)

    # 1. LanceDB Storage Backend with explicit path & table
    lancedb_backend = LanceDBStorage(
        path=storage_directory,
        table_name="enterprise_agent_memory",
        vector_dim=1536,  # Default dimension for text-embedding-3-small
    )

    # 2. Unified Memory configuration
    memory_engine = Memory(
        storage=lancedb_backend,
        semantic_weight=0.5,           # 50% weight on embedding similarity
        recency_weight=0.3,            # 30% weight on how recent the memory is
        importance_weight=0.2,         # 20% weight on importance rating
        recency_half_life_days=7.0,    # Halve recency score every 7 days
        default_importance=0.6,
        confidence_threshold_high=0.75,
        confidence_threshold_low=0.30,
    )
    return memory_engine


# ==============================================================================
# SECTION 3: DEMONSTRATION RUN
# ==============================================================================
def run_advanced_memory_demo():
    print("\n" + "=" * 70)
    print("ADVANCED CREWAI MEMORY: LANCEDB PERSISTENCE & SCOPED STORAGE")
    print("=" * 70)

    db_path = str(Path(__file__).parent / ".memory_store_lancedb")
    print(f"[INFO] Initializing persistent LanceDB at: {db_path}")

    # Build custom memory engine
    unified_memory = create_lancedb_backed_memory(storage_directory=db_path)

    # Agent 1: Customer Support Triage
    support_agent = Agent(
        role="Tier-2 Technical Account Manager",
        goal="Remember customer infrastructure preferences and previous SLA constraints",
        backstory=(
            "You manage enterprise client relationships. You retain exact details "
            "about client architecture, region requirements, and security policies across sessions."
        ),
        verbose=True,
    )

    # Agent 2: Solution Architect
    architect_agent = Agent(
        role="Cloud Infrastructure Deployer",
        goal="Design infrastructure solutions strictly respecting customer constraints from memory",
        backstory="You rely heavily on memory context recalled from account management notes.",
        verbose=True,
    )

    # Task 1: Record critical customer facts into memory
    ingestion_task = Task(
        description=(
            "Log the following customer profile into memory: "
            "Client 'OmniCorp' requires all workloads in AWS region 'eu-central-1', "
            "forbids public S3 buckets, and requires 99.99% multi-AZ RDS PostgreSQL. "
            "Confirm the profile is committed."
        ),
        expected_output="Confirmation of registered client constraints.",
        agent=support_agent,
    )

    # Task 2: Recall and plan
    planning_task = Task(
        description=(
            "Recall OmniCorp's architectural constraints stored in memory and write a 2-point "
            "infrastructure deployment checklist adhering to their required region and database specs."
        ),
        expected_output="A 2-point deployment checklist referencing OmniCorp's recalled requirements.",
        agent=architect_agent,
    )

    # Assemble crew with configured Memory
    crew = Crew(
        agents=[support_agent, architect_agent],
        tasks=[ingestion_task, planning_task],
        process=Process.sequential,
        memory=unified_memory,  # Injects our customized LanceDB Memory engine!
        verbose=True,
    )

    result = crew.kickoff()
    print("\n--- ADVANCED MEMORY EXECUTION RESULT ---")
    print(result)

    # Inspect the persistent records stored in LanceDB
    print("\n[INFO] Validating records stored in LanceDB backend...")
    saved_records = unified_memory.storage.list_records(limit=10)
    print(f"Total memory records committed in storage: {len(saved_records)}")
    for i, r in enumerate(saved_records[:3], 1):
        print(f"  [{i}] ID: {r.id[:8]}... | Scope: {r.scope} | Content: {r.content[:70]}...")

    return result


if __name__ == "__main__":
    run_advanced_memory_demo()
