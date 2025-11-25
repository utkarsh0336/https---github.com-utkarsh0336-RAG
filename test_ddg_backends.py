from duckduckgo_search import DDGS

queries = [
    "What is the latest iPhone model?",
    "current iPhone models",
    "Sigmoid Function definition"
]

print("Testing DDGS backends...")

backends = ["api", "html", "lite"]

for backend in backends:
    print(f"\n--- Testing backend: {backend} ---")
    try:
        with DDGS() as ddgs:
            for q in queries:
                print(f"Query: {q}")
                results = list(ddgs.text(q, max_results=3, backend=backend))
                if results:
                    print(f"First result: {results[0]['title']}")
                else:
                    print("No results found.")
    except Exception as e:
        print(f"Error with {backend}: {e}")
