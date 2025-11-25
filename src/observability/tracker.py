import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import threading

class RAGTracker:
    """Custom tracker for RAG pipeline observability."""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.current_run = None
        self.lock = threading.Lock()
        
    def start_run(self, question: str) -> str:
        """Start tracking a new query run."""
        run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        with self.lock:
            self.current_run = {
                "run_id": run_id,
                "question": question,
                "start_time": time.time(),
                "steps": [],
                "metrics": {
                    "total_tokens": 0,
                    "retrieval_time": 0,
                    "generation_time": 0,
                    "total_time": 0
                },
                "final_answer": None,
                "cache_hit": False
            }
        
        return run_id
    
    def log_retrieval(self, source: str, query: str, results: List[Dict], scores: Optional[List[float]] = None):
        """Log retrieval results with scores."""
        if not self.current_run:
            return
            
        with self.lock:
            self.current_run["steps"].append({
                "step": "retrieval",
                "source": source,
                "query": query,
                "num_results": len(results),
                "results": [
                    {
                        "text": r.get("text", r.get("page_content", ""))[:200],
                        "metadata": r.get("metadata", {}),
                        "score": scores[i] if scores and i < len(scores) else None
                    }
                    for i, r in enumerate(results[:5])  # Log top 5
                ],
                "timestamp": time.time()
            })
    
    def log_generation(self, answer: str, tokens: int = 0):
        """Log answer generation."""
        if not self.current_run:
            return
            
        with self.lock:
            self.current_run["steps"].append({
                "step": "generation",
                "answer": answer,
                "tokens": tokens,
                "timestamp": time.time()
            })
            self.current_run["metrics"]["total_tokens"] += tokens
    
    def log_validation(self, report: Dict):
        """Log validation report."""
        if not self.current_run:
            return
            
        with self.lock:
            self.current_run["steps"].append({
                "step": "validation",
                "is_complete": report.get("is_complete"),
                "is_outdated": report.get("is_outdated"),
                "score": report.get("score"),
                "gaps": report.get("gaps", []),
                "inconsistencies": report.get("inconsistencies", []),
                "search_queries": report.get("search_queries", []),
                "reasoning": report.get("reasoning"),
                "timestamp": time.time()
            })
    
    def log_tool_call(self, tool_name: str, input_query: str, result: str, success: bool = True):
        """Log tool execution."""
        if not self.current_run:
            return
            
        with self.lock:
            self.current_run["steps"].append({
                "step": "tool_call",
                "tool_name": tool_name,
                "input": input_query,
                "result": result[:500],  # Truncate long results
                "success": success,
                "timestamp": time.time()
            })
    
    def log_synthesis(self, final_answer: str, sources_used: List[str], tokens: int = 0):
        """Log final synthesis."""
        if not self.current_run:
            return
            
        with self.lock:
            self.current_run["steps"].append({
                "step": "synthesis",
                "final_answer": final_answer,
                "sources_used": sources_used,
                "tokens": tokens,
                "timestamp": time.time()
            })
            self.current_run["metrics"]["total_tokens"] += tokens
            self.current_run["final_answer"] = final_answer
    
    def log_cache_hit(self, answer: str):
        """Log cache hit."""
        if not self.current_run:
            return
            
        with self.lock:
            self.current_run["cache_hit"] = True
            self.current_run["final_answer"] = answer
    
    def end_run(self) -> Dict:
        """End run and save log."""
        if not self.current_run:
            return {}
            
        with self.lock:
            self.current_run["end_time"] = time.time()
            self.current_run["metrics"]["total_time"] = (
                self.current_run["end_time"] - self.current_run["start_time"]
            )
            
            # Save to file
            log_file = self.log_dir / f"{self.current_run['run_id']}.json"
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_run, f, indent=2, ensure_ascii=False)
            
            run_data = self.current_run
            self.current_run = None
            return run_data
    
    def get_summary_stats(self) -> Dict:
        """Get summary statistics from all logs."""
        all_logs = list(self.log_dir.glob("*.json"))
        
        if not all_logs:
            return {}
        
        total_runs = len(all_logs)
        cache_hits = 0
        avg_time = 0
        avg_tokens = 0
        
        for log_file in all_logs:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get("cache_hit"):
                        cache_hits += 1
                    avg_time += data.get("metrics", {}).get("total_time", 0)
                    avg_tokens += data.get("metrics", {}).get("total_tokens", 0)
            except:
                continue
        
        return {
            "total_runs": total_runs,
            "cache_hits": cache_hits,
            "cache_hit_rate": cache_hits / total_runs if total_runs > 0 else 0,
            "avg_response_time": avg_time / total_runs if total_runs > 0 else 0,
            "avg_tokens_per_run": avg_tokens / total_runs if total_runs > 0 else 0
        }

# Global tracker instance
_tracker = None

def get_tracker() -> RAGTracker:
    """Get or create global tracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = RAGTracker()
    return _tracker
