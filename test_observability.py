import sys
import os
sys.path.append(os.path.abspath('.'))

from src.observability import get_tracker

print("Testing RAG Observability System...")

tracker = get_tracker()

# Simulate a query run
run_id = tracker.start_run("What is a transformer in AI?")
print(f"\n✓ Started run: {run_id}")

# Simulate retrieval
tracker.log_retrieval("wiki_rag", "transformer", 
                     [{"text": "A transformer is...", "metadata": {"source": "wiki"}}],
                     scores=[0.95])
print("✓ Logged retrieval")

# Simulate generation
tracker.log_generation("A transformer is a deep learning architecture...", tokens=150)
print("✓ Logged generation")

# Simulate validation
tracker.log_validation({
    "is_complete": True,
    "is_outdated": False,
    "score": 0.9,
    "gaps": [],
    "inconsistencies": [],
    "search_queries": [],
    "reasoning": "Answer is complete and accurate"
})
print("✓ Logged validation")

# Simulate tool call
tracker.log_tool_call("web_search", "latest transformer models", "GPT-4, Claude 3...", success=True)
print("✓ Logged tool call")

# Simulate synthesis
tracker.log_synthesis("Final comprehensive answer...", ["VectorDB", "Web"], tokens=200)
print("✓ Logged synthesis")

# End run
result = tracker.end_run()
print(f"\n✓ Run completed and saved to: logs/{result['run_id']}.json")

# Show stats
stats = tracker.get_summary_stats()
print(f"\n=== Overall Statistics ===")
print(f"Total runs: {stats.get('total_runs', 0)}")
print(f"Cache hit rate: {stats.get('cache_hit_rate', 0):.1%}")
print(f"Avg response time: {stats.get('avg_response_time', 0):.2f}s")
print(f"Avg tokens per run: {stats.get('avg_tokens_per_run', 0):.0f}")

print("\n✅ Observability system is operational!")
