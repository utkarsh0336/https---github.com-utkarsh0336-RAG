# RAG System Workflow Explanation

This document breaks down the code flow of your Self-Correcting RAG system, starting from the user interface (`app.py`) down to the core logic (`graph.py` and `retrieval.py`).

---

## Part 1: The User Interface (`src/ui/app.py`)

This file is the entry point. It runs a Streamlit web application.

### 1. Setup and Imports (Lines 1-18)
```python
import os
import sys
from dotenv import load_dotenv
# ... imports ...
load_dotenv()  # Loads environment variables from .env (API keys, DB URLs)
sys.path.append(...) # Adds project root to python path so we can import 'src' modules
import streamlit as st
from src.agents.graph import RAGGraph # IMPORTING THE CORE BRAIN
```
- **Key Action**: It sets up the environment and imports `RAGGraph`, which is the class that controls the entire AI pipeline.

### 2. Initialization (Lines 26-32)
```python
if "graph" not in st.session_state:
    try:
        st.session_state.graph = RAGGraph() # Initialize the AI Graph ONCE
        st.success("✅ System initialized successfully!")
    except Exception as e:
        # ... error handling ...
```
- **Logic**: Streamlit reruns the script on every interaction. We use `st.session_state` to ensure we only initialize the heavy `RAGGraph` class once.

### 3. User Input & Execution (Lines 58-70)
```python
col1, col2 = st.columns([3, 1])
with col1:
    question = st.text_input("Ask a question:", ...) # User types here

if st.button("🚀 Run Query", type="primary"): # User clicks button
    if question:
        with st.spinner("Processing..."):
            try:
                # THIS IS THE TRIGGER POINT
                result = st.session_state.graph.run(question) 
```
- **Critical Line**: `result = st.session_state.graph.run(question)`
- This passes the user's question to the `RAGGraph` instance. The UI waits here until the graph finishes its work.

---

## Part 2: The Orchestrator (`src/agents/graph.py`)

This file defines the "Brain" using LangGraph. It decides what steps to take (Retrieve -> Generate -> Validate).

### 1. State Definition (Lines 11-18)
```python
class GraphState(TypedDict):
    question: str
    context: str
    initial_answer: str
    validation_report: dict
    new_info: str
    final_answer: str
```
- **Concept**: This dictionary is the "Memory" of a single run. As the graph moves from node to node, they pass this state around, adding information to it.

### 2. The `RAGGraph` Class & Setup (Lines 20-61)
```python
class RAGGraph:
    def __init__(self):
        # Initialize all the specialized agents
        self.retriever = MultiSourceRetriever()
        self.generator = AnswerGenerator()
        self.validator = ValidationAgent()
        # ...
        
        # BUILD THE WORKFLOW
        self.workflow = StateGraph(GraphState)
        
        # Add Nodes (The workers)
        self.workflow.add_node("retrieve", self.retrieve_node)
        self.workflow.add_node("generate", self.generate_node)
        # ...
        
        # Define the Path (Edges)
        self.workflow.set_entry_point("retrieve") # Start here
        self.workflow.add_edge("retrieve", "generate") # Then go here
        self.workflow.add_edge("generate", "validate") # Then go here
        
        # Conditional Logic (The Decision)
        self.workflow.add_conditional_edges(
            "validate",
            self.check_validation, # Run this function to decide where to go next
            {
                "accepted": END,       # If good, stop.
                "needs_work": "execute" # If bad, go to 'execute' (search web)
            }
        )
```

### 3. The `run` Method (Lines 147-181)
This is what `app.py` called.
```python
def run(self, question: str):
    # 1. Check Cache (Fast Path)
    if self.cache:
        cached_answer = self.cache.get_answer(question)
        if cached_answer:
            return {"final_answer": cached_answer, ...}
            
    # 2. Run the Graph (Slow Path)
    inputs = {"question": question}
    result = self.app.invoke(inputs) # Starts the LangGraph execution
    
    # 3. Cache the result for next time
    if self.cache:
        self.cache.set_answer(question, result["final_answer"])
        
    return result
```

### 4. The Node Functions (The Actual Work)

#### A. `retrieve_node` (Lines 63-73)
```python
def retrieve_node(self, state: GraphState):
    docs = self.retriever.retrieve(state["question"]) # Call retrieval.py
    context = "\n\n".join([d.page_content for d in docs])
    return {"context": context} # Updates state['context']
```

#### B. `generate_node` (Lines 75-83)
```python
def generate_node(self, state: GraphState):
    # Uses context from previous step to generate answer
    answer = self.generator.generate(state["question"], state["context"])
    return {"initial_answer": answer} # Updates state['initial_answer']
```

#### C. `validate_node` (Lines 85-105)
```python
def validate_node(self, state: GraphState):
    # Checks if the answer is good
    report = self.validator.validate(...)
    return {"validation_report": report}
```

---

## Part 3: The Retrieval Logic (`src/rag/retrieval.py`)

This is called by `retrieve_node` in the graph.

### 1. `HybridRetriever` (Lines 8-84)
This class handles searching a specific collection (like Wiki or Arxiv).
```python
def search(self, query: str, k: int = 10):
    # 1. Check Vector Cache
    if self.cache: ...
    
    # 2. Create Embedding
    query_vector = self.model.encode(query).tolist()
    
    # 3. Qdrant Search (Dense Vector Search)
    results = self.client.query_points(...)
    
    # 4. Re-ranking (CrossEncoder) - CRITICAL STEP
    # It takes the top results and uses a more powerful model to sort them
    scores = self.reranker.predict(passages)
    ranked_results = sorted(...)
    
    return top_k_results
```

### 2. `MultiSourceRetriever` (Lines 85-104)
This simply bundles multiple retrievers together.
```python
class MultiSourceRetriever:
    def __init__(self):
        self.wiki_retriever = HybridRetriever("wiki_rag")
        self.arxiv_retriever = HybridRetriever("arxiv_rag")
        
    def retrieve(self, query: str):
        # Queries both sources and combines results
        docs = []
        docs.extend(self.wiki_retriever.search(query))
        docs.extend(self.arxiv_retriever.search(query))
        return docs
```

---

## Summary of the Flow

1. **User** types question in `app.py`.
2. `app.py` calls `graph.run(question)`.
3. `graph.run` checks **Redis Cache**. If hit, returns immediately.
4. If miss, it starts the **LangGraph**:
   - **Retrieve**: `retrieval.py` searches Qdrant (Wiki/Arxiv), re-ranks with CrossEncoder.
   - **Generate**: LLM creates an answer using retrieved docs.
   - **Validate**: `ValidationAgent` checks if the answer is accurate/complete.
   - **Check**: 
     - If **Good**: End.
     - If **Bad**: Go to `Execute` (Web Search) -> `Synthesize` (Combine info).
5. Result is returned to `app.py` and displayed to the user.
