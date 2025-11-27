# Technical Design Document: Self-Correcting RAG System

## 1. Architectural Choices

The system is designed as a modular, agentic RAG (Retrieval-Augmented Generation) pipeline that prioritizes accuracy and self-correction.

### Core Components
- **Orchestration (LangGraph)**: Chosen for its ability to define stateful, cyclic workflows. Unlike linear chains, LangGraph allows the system to loop back (e.g., from Validation to Execution) to correct errors dynamically.
- **Vector Database (Qdrant)**: Selected for its performance and ease of local deployment (via Docker). It handles dense vector similarity search efficiently.
- **Caching (Redis)**: Implemented to reduce latency and API costs. A two-tier strategy caches both final answers and expensive embedding computations.
- **User Interface (Streamlit)**: Provides a rapid, interactive frontend for testing and demonstrating the system's capabilities.

### Design Principles
- **Modularity**: Components (Retrieval, Generation, Validation, Execution) are isolated in the `src/agents` and `src/rag` directories, allowing for independent testing and upgrades.
- **Observability**: Integrated tracking (via `src/observability`) ensures every step of the pipeline (retrieval, generation, validation) is logged for debugging and evaluation.

---

## 2. Agentic Workflow

The workflow is defined in `src/agents/graph.py` and follows a "Retrieve-Generate-Validate-Correct" pattern.

### State Management
The `GraphState` dictionary tracks the lifecycle of a query:
- `question`: User's input.
- `context`: Retrieved documents.
- `initial_answer`: First draft from the LLM.
- `validation_report`: Quality assessment of the answer.
- `new_info`: Data fetched from external sources (web) during correction.
- `final_answer`: The approved response.

### Workflow Steps (Nodes)
1.  **Retrieve (`retrieve_node`)**:
    -   Fetches relevant documents from the internal knowledge base (Qdrant).
    -   Updates `context`.
2.  **Generate (`generate_node`)**:
    -   Synthesizes an answer using the retrieved context.
    -   Updates `initial_answer`.
3.  **Validate (`validate_node`)**:
    -   Evaluates the `initial_answer` for completeness, accuracy, and relevance.
    -   Produces a `validation_report`.
4.  **Decision Point (`check_validation`)**:
    -   **Accepted**: If the score is > 0.8 and not outdated -> End workflow.
    -   **Needs Work**: If gaps are found or info is outdated -> Proceed to **Execute**.
5.  **Execute (`execute_node`)**:
    -   Triggered only if validation fails.
    -   Performs web searches to fill identified gaps.
    -   Updates `new_info`.
6.  **Synthesize (`synthesize_node`)**:
    -   Combines the original context with `new_info` to produce a corrected answer.
    -   Updates `final_answer`.

---

## 3. Caching Strategy

The system employs a robust **Two-Tier Caching System** using Redis (`src/cache/redis_cache.py`) to optimize performance.

### Tier 1: Answer Cache (High Level)
-   **Purpose**: Returns instant responses for identical, previously asked questions.
-   **Key**: `answer:{hash(question)}`
-   **TTL (Time-To-Live)**:
    -   **Standard**: 1 hour (3600s).
    -   **Web-Sourced**: 30 minutes (1800s) – shorter duration for dynamic data fetched from the web.

### Tier 2: Vector Cache (Low Level)
-   **Purpose**: Avoids re-computing embeddings for the same text, saving CPU/GPU resources and latency.
-   **Key**: `vector:{hash(text)}`
-   **TTL**: 24 hours (86400s) – embeddings are stable and rarely change.
-   **Mechanism**: Before calling the embedding model, the system checks Redis. If a hit occurs, the stored vector is deserialized (pickle) and used immediately.

---

## 4. Re-ranking Algorithm

The retrieval process (`src/rag/retrieval.py`) uses a **Hybrid Retrieval + Re-ranking** approach to ensure high relevance.

### Step 1: Dense Retrieval (Recall)
-   **Model**: `all-MiniLM-L6-v2` (SentenceTransformer).
-   **Process**: The query is embedded into a vector and compared against the Qdrant index.
-   **Oversampling**: The system retrieves `2 * k` (e.g., 20) candidates, intentionally fetching more than needed to ensure the correct answer is likely included.

### Step 2: Cross-Encoder Re-ranking (Precision)
-   **Model**: `cross-encoder/ms-marco-MiniLM-L-6-v2`.
-   **Process**:
    1.  The system constructs pairs of `(query, document_text)` for all candidates.
    2.  The Cross-Encoder scores each pair based on how well the document answers the specific query. Unlike bi-encoders (vector similarity), cross-encoders look at the full interaction between query and document terms.
    3.  Results are sorted by this new score.
-   **Output**: The top `k` (e.g., 10) highest-scored documents are returned to the generator.

### Why this matters?
Vector search is fast but can miss nuances. The Cross-Encoder is slower but much more accurate. By using vector search to filter the universe of documents down to a small set (20), and then using the Cross-Encoder to pick the best ones, we get the **speed of vector search with the accuracy of BERT-based ranking**.
