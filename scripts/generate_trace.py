import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.graph import RAGGraph

def generate_trace():
    # Check for LangSmith configuration
    if not os.getenv("LANGCHAIN_API_KEY"):
        print("⚠️  LANGCHAIN_API_KEY not found in environment variables.")
        print("Please set LANGCHAIN_API_KEY, LANGCHAIN_TRACING_V2=true, and LANGCHAIN_PROJECT in your .env file.")
        return

    print("🚀 Initializing RAG Graph...")
    rag = RAGGraph()
    
    question = "What is the architecture of this RAG system?"
    print(f"❓ Running query: {question}")
    
    try:
        result = rag.run(question)
        print("\n✅ Query completed successfully!")
        print(f"Answer: {result.get('final_answer')[:100]}...")
        print("\n🔍 Check your LangSmith project for the trace.")
        
        # Print trace URL if available (requires langchain-core >= 0.2)
        # This is a best-effort attempt to show the URL
        project = os.getenv("LANGCHAIN_PROJECT", "default")
        print(f"🔗 Project URL: https://smith.langchain.com/o/me/projects/p/{project}")
        
    except Exception as e:
        print(f"❌ Error running query: {e}")

if __name__ == "__main__":
    generate_trace()
