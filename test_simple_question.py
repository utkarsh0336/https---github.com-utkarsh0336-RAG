import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.graph import RAGGraph

def simple_test():
    print("Testing simple question...")
    graph = RAGGraph()
    
    question = "What is the capital of USA?"
    print(f"Question: {question}\n")
    
    result = graph.run(question)
    
    print("\n--- RESULT ---")
    print(f"Keys: {result.keys()}")
    print(f"\nInitial Answer: {result.get('initial_answer', 'MISSING')[:200]}")
    print(f"\nValidation Report: {result.get('validation_report', 'MISSING')}")
    print(f"\nFinal Answer: {result.get('final_answer', 'MISSING')}")
    
    # Save full result to file for inspection
    with open("test_result.txt", "w", encoding="utf-8") as f:
        f.write(f"Question: {question}\n\n")
        f.write(f"Initial Answer:\n{result.get('initial_answer', 'MISSING')}\n\n")
        f.write(f"Validation:\n{result.get('validation_report', 'MISSING')}\n\n")
        if 'new_info' in result:
            f.write(f"New Info:\n{result.get('new_info')}\n\n")
        f.write(f"Final Answer:\n{result.get('final_answer', 'MISSING')}\n")

if __name__ == "__main__":
    simple_test()
