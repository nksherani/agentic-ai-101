# Deep Dive: CrewAI Memory Architecture & Storage Backends

This guide explains how **Memory** works under the hood in CrewAI 1.x, how memory records are scored and scoped, and how to plug in different storage engines (LanceDB, Qdrant, SQLite, Redis, or custom vector stores).

See the companion runnable code in [`level_3_advanced_memory_storage.py`](file:///Volumes/Lexar/GitHub/agentic-ai-101/crewai-demo/level_3_advanced_memory_storage.py).

---

## 1. Evolution of Memory in CrewAI

In early CrewAI versions, memory was split into three separate classes:
* `ShortTermMemory` (in-memory ChromaDB)
* `LongTermMemory` (SQLite file)
* `EntityMemory` (Entity extraction storage)

In current CrewAI (1.x), memory has been consolidated into a **Unified Memory Engine** (`crewai.memory.unified_memory.Memory`). This engine manages memory lifecycles through:
1. **Dynamic Composite Scoring**: Balancing semantic similarity, temporal recency, and importance ratings.
2. **Hierarchical Scopes**: Isolating memories across agents, crews, tasks, and users.
3. **Pluggable Storage Backends**: Decoupling the memory reasoning logic from the underlying database through the `StorageBackend` protocol.

---

## 2. The Storage Engine Architecture

```
                  ┌──────────────────────────────────────────────┐
                  │                 Crew / Agent                 │
                  └──────────────────────┬───────────────────────┘
                                         │
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │        Unified Memory Engine (Memory)        │
                  │  - Composite Scoring (Semantic + Recency)    │
                  │  - Hierarchical Scoping (/crew/agent/...)     │
                  │  - Embedder Pipeline                         │
                  └──────────────────────┬───────────────────────┘
                                         │
                  ┌──────────────────────┴───────────────────────┐
                  ▼                                              ▼
┌───────────────────────────────────┐          ┌───────────────────────────────────┐
│     Default Embedded Storage      │          │      Custom Storage Backend       │
│  - LanceDB (Local vector files)   │          │  - Redis / pgvector / Qdrant      │
│  - SQLite (Entity/run tracking)   │          │  - Satisfies `StorageBackend`     │
└───────────────────────────────────┘          └───────────────────────────────────┘
```

---

## 3. How Memory Retrieval Works: Composite Scoring

When an agent needs context, CrewAI searches stored records using a **composite score** ($S_{total}$) rather than simple cosine similarity:

$$S_{total} = (w_{sem} \times S_{sem}) + (w_{rec} \times S_{rec}) + (w_{imp} \times S_{imp})$$

Where:
* **$S_{sem}$ (Semantic Relevance)**: Vector cosine similarity between the query embedding and memory records.
* **$S_{rec}$ (Recency Decay)**: Exponential half-life decay. Memories fade over time unless refreshed:
  $$S_{rec} = e^{-\frac{\Delta t \cdot \ln(2)}{t_{half}}}$$
* **$S_{imp}$ (Importance Weight)**: How critical the agent or system flagged this piece of information when stored.

You can tune these directly in code:
```python
from crewai.memory.unified_memory import Memory
from crewai.memory.storage.lancedb_storage import LanceDBStorage

custom_memory = Memory(
    storage=LanceDBStorage(path="./my_memory_db", vector_dim=1536),
    semantic_weight=0.5,           # 50% vector similarity
    recency_weight=0.3,            # 30% favor newer memories
    importance_weight=0.2,         # 20% favor high-impact facts
    recency_half_life_days=7.0,    # Halve relevance every 7 days
)
```

---

## 4. Comparing Storage Backends

| Storage Engine | Best Used For | Persistence | Setup Complexity |
| :--- | :--- | :--- | :--- |
| **LanceDB (Default)** | Local development, edge apps, fast serverless vector search | Local disk / S3 | Zero setup (embedded in python) |
| **Qdrant Edge** | High-concurrency agent systems, hybrid search (keyword + vector) | Remote / Cluster | Requires Qdrant server or Qdrant Cloud |
| **Redis (Vector/Key-Val)** | Real-time multi-agent systems, low-latency session caching | In-memory + RDB | Requires Redis 7+ with RedisSearch module |
| **PostgreSQL (`pgvector`)** | Enterprise stacks already running Postgres, relational + vector joins | Relational Disk | Requires `pgvector` extension |
| **Custom `StorageBackend`** | Proprietary DBs, corporate search APIs, in-memory mock testing | Custom | Implement the `StorageBackend` protocol |

---

## 5. Implementing a Custom Storage Backend

Any storage engine can be plugged into CrewAI by implementing the `StorageBackend` protocol (found in `crewai.memory.storage.backend`).

The required interface consists of:
```python
from crewai.memory import MemoryRecord, ScopeInfo
from crewai.memory.storage.backend import StorageBackend

class CustomPostgresVectorStorage(StorageBackend):
    def save(self, records: list[MemoryRecord]) -> None:
        """Insert records and vector embeddings into database."""
        pass

    def search(
        self,
        query_embedding: list[float],
        scope_prefix: str | None = None,
        categories: list[str] | None = None,
        metadata_filter: dict | None = None,
        limit: int = 10,
        min_score: float = 0.0,
    ) -> list[tuple[MemoryRecord, float]]:
        """Vector KNN / Cosine similarity query."""
        pass

    def get_record(self, record_id: str) -> MemoryRecord | None: ...
    def list_records(self, scope_prefix: str | None = None, limit: int = 200, offset: int = 0) -> list[MemoryRecord]: ...
    def update(self, record: MemoryRecord) -> None: ...
    def delete(self, **kwargs) -> int: ...
    def count(self, scope_prefix: str | None = None) -> int: ...
    def reset(self, scope_prefix: str | None = None) -> None: ...
    def get_scope_info(self, scope: str) -> ScopeInfo: ...
    def list_scopes(self, parent: str = "/") -> list[str]: ...
    def list_categories(self, scope_prefix: str | None = None) -> dict[str, int]: ...
```

---

## 6. Global Storage Factory Injection

If you want **all crews and agents** across your application to use your custom storage backend by default without passing it into every `Crew(memory=...)`, you can set a global storage factory:

```python
from crewai.memory.storage.factory import set_memory_storage_factory

def my_custom_factory(config=None):
    return LanceDBStorage(path="./shared_enterprise_memories")
    # Or: return CustomPostgresVectorStorage(...)

set_memory_storage_factory(my_custom_factory)
```

Now, any crew created with `Crew(..., memory=True)` will automatically use your custom storage backend.
