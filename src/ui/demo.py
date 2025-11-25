import streamlit as st
import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.rag.generation import LLMClient

st.set_page_config(page_title="Self-Correcting RAG - Demo", layout="wide")

st.title("🤖 Self-Correcting RAG System - Simple Demo")
st.markdown("""
This is a simplified demo that works without the full vector database.
It demonstrates the LLM integration with Ollama (Llama 3.2).
""")

# Initialize LLM
if "llm" not in st.session_state:
    try:
        st.session_state.llm = LLMClient(model_name="llama3.2:1b").llm
        st.success("✅ Connected to Ollama (llama3.2:1b)")
    except Exception as e:
        st.error(f"❌ Failed to connect to Ollama: {e}")
        st.stop()

question = st.text_input("Ask a question:", "What is a transformer model in AI?")

if st.button("Generate Answer"):
    with st.spinner("Generating answer..."):
        try:
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_core.output_parsers import StrOutputParser
            
            prompt = ChatPromptTemplate.from_template("""
            You are an expert AI assistant. Answer the following question concisely and accurately.
            
            Question: {question}
            
            Answer:
            """)
            
            chain = prompt | st.session_state.llm | StrOutputParser()
            answer = chain.invoke({"question": question})
            
            st.subheader("Answer:")
            st.success(answer)
            
        except Exception as e:
            st.error(f"An error occurred: {e}")

st.markdown("---")
st.markdown("""
### 📝 Next Steps to Enable Full RAG:
1. Start Qdrant: `docker-compose up -d qdrant redis`
2. Run data ingestion: `python scripts/setup_sql.py`
3. Ingest Wikipedia data: `python scripts/ingest_wiki.py` (takes ~30 min)
4. Ingest ArXiv data: `python scripts/ingest_arxiv.py` (takes ~20 min)
5. Run the full app: `streamlit run src/ui/app.py`
""")
