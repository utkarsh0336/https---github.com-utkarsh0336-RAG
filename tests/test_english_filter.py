from src.agents.tools import web_search_tool

query = "Which benchmarks are used to evaluate machine learning models in NLP?"
print(f"Testing web search with English filtering...")
print(f"Query: {query}\n")

result = web_search_tool.invoke(query)
print(f"Result:\n{result[:500]}...")

# Check if result contains non-English content
if "知乎" in result or any(ord(c) > 127 for c in result[:100]):
    print("\nWARNING: Non-English content detected!")
else:
    print("\nSUCCESS: English-only results!")
