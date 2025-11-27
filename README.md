# Self-Correcting RAG System

A robust, agentic Retrieval-Augmented Generation (RAG) system built with **LangGraph**, **Qdrant**, and **Redis**. This project implements a self-correcting workflow that retrieves information from multiple sources (Wikipedia, ArXiv), validates the generated answers, and dynamically fetches missing information if needed.

## 🚀 Key Features

*   **Agentic Workflow**: Powered by **LangGraph**, the system orchestrates a multi-step process: Retrieval -> Generation -> Validation -> Execution (if needed) -> Synthesis.
*   **Multi-Source Retrieval**: Simultaneously searches **Wikipedia** and **ArXiv** for comprehensive context.
*   **Hybrid Search & Re-ranking**: Combines dense vector search (Qdrant) with keyword matching and refines results using a Cross-Encoder for high precision.
*   **Self-Correction**: A dedicated **Validation Agent** critiques answers. If an answer is incomplete or outdated, the **Execution Agent** performs active web research to fill the gaps.
*   **Two-Tier Caching**:
    *   **Tier 1**: Caches final answers in **Redis** (1-hour TTL) for instant responses to repeated queries.
    *   **Tier 2**: Caches vector embeddings (24-hour TTL) to save computation costs.
*   **Observability**: Tracks every step of the pipeline for debugging and performance monitoring.

## 🛠️ Tech Stack

*   **Core**: Python 3.9+, LangChain, LangGraph
*   **Vector Database**: Qdrant
*   **Caching**: Redis
*   **LLM**: Ollama (Local) / OpenAI (Optional)
*   **UI**: Streamlit
*   **Containerization**: Docker & Docker Compose

## 📋 Prerequisites

*   [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed.
*   [Ollama](https://ollama.com/) installed and running locally (for local LLM support).
    *   Pull the model: `ollama pull mistral` (or your preferred model).

## ⚡ Quick Start (Docker)

The easiest way to run the system is using Docker Compose.

1.  **Clone the Repository**
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Configure Environment**
    Create a `.env` file in the root directory:
    ```env
    # LLM Configuration
    OLLAMA_BASE_URL=http://host.docker.internal:11434
    LLM_MODEL=mistral

    # Search API (Optional, for fallback web search)
    SERPER_API_KEY=your_serper_api_key
    TAVILY_API_KEY=your_tavily_api_key
    ```

3.  **Run with Docker Compose**
    ```bash
    docker-compose up --build
    ```
    *   The application will be available at `http://localhost:8501`.
    *   Qdrant dashboard: `http://localhost:6333/dashboard`.

## 📦 Local Installation

If you prefer to run without Docker:

1.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Start Infrastructure**
    Ensure you have local instances of **Qdrant** (port 6333) and **Redis** (port 6379) running.

3.  **Run the Application**
    ```bash
    streamlit run src/ui/app.py
    ```

## 🏗️ Architecture

The system follows a cyclic graph architecture:

1.  **Retrieve**: Fetches documents from Qdrant (Wiki/ArXiv).
2.  **Generate**: LLM drafts an initial answer.
3.  **Validate**: Checks the answer for accuracy, completeness, and timeliness.
    *   *Pass*: Returns the answer.
    *   *Fail*: Triggers the **Execute** phase.
4.  **Execute**: Generates search queries to find missing information (Web Search).
5.  **Synthesize**: Merges the initial draft with new findings to produce the final answer.

## 📂 Project Structure

```
├── data/               # Local data storage
├── scripts/            # Ingestion scripts (Wiki, ArXiv, SQL)
├── src/
│   ├── agents/         # LangGraph agents (Graph, Validation, Execution, etc.)
│   ├── cache/          # Redis caching logic
│   ├── rag/            # Retrieval and Generation logic (Qdrant, Hybrid Search)
│   ├── ui/             # Streamlit application
│   └── utils/          # Helper functions
├── docker-compose.yml  # Docker services config
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.
