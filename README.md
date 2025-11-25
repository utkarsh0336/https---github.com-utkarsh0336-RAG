# Self-Correcting RAG System

A dynamic, agentic Retrieval-Augmented Generation system that can self-correct, gather information from multiple sources (VectorDB, Web, SQL), and synthesize verified answers.

## Core Features
- **Hybrid Retrieval**: Combines vector and keyword search for high recall.
- **Self-Correction**: A "Validation Agent" critiques initial answers and identifies gaps.
- **Autonomous Execution**: An "Execution Agent" uses tools (Web Search, ArXiv, SQL) to fill those gaps.
- **Multi-Source Synthesis**: Combines data from Wikipedia, ArXiv, and SQL databases.
- **Advanced Caching**: Two-tier Redis caching for queries and vectors.

## Architecture
- **Orchestration**: LangGraph
- **Vector DB**: Qdrant
- **LLM**: Llama 3 / Mixtral (via API/TGI)
- **Frontend**: Streamlit

## Setup
1. Clone the repository.
2. Run `docker-compose up --build`.
3. Access the UI at `http://localhost:8501`.
