"""
Automated Evaluation Pipeline

Runs the RAG system on all evaluation questions and generates a report.
"""

import sys
import os
sys.path.append(os.path.abspath('.'))

import json
from datetime import datetime
from pathlib import Path
from src.agents.graph import RAGGraph
from src.evaluation import EVAL_QUESTIONS, RAGEvaluator
from dotenv import load_dotenv

load_dotenv()

def run_evaluation(sample_size: int = 10):
    """Run automated evaluation on the dataset."""
    
    print("🚀 Starting RAG System Evaluation")
    print(f"Evaluation dataset: {len(EVAL_QUESTIONS)} questions")
    print("=" * 60)
    
    # Initialize
    graph = RAGGraph()
    evaluator = RAGEvaluator()
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_questions": min(sample_size, len(EVAL_QUESTIONS)),
        "questions_evaluated": [],
        "aggregate_scores": {
            "faithfulness": [],
            "relevance": [],
            "citation_accuracy": [],
            "overall": []
        }
    }
    
    # Run each question
    for i, q_data in enumerate(EVAL_QUESTIONS[:sample_size]):
        print(f"\n📝 Question {i+1}/{sample_size}: {q_data['question'][:60]}...")
        
        try:
            # Run RAG pipeline
            result = graph.run(q_data["question"])
            answer = result.get("final_answer", "")
            context = result.get("context", "")
            
            # Evaluate
            eval_result = evaluator.evaluate_answer(
                question=q_data["question"],
                answer=answer,
                context=context,
                sources_used=[]
            )
            
            # Store results
            q_result = {
                "id": q_data["id"],
                "question": q_data["question"],
                "answer": answer[:200] + "..." if len(answer) > 200 else answer,
                "required_sources": q_data["required_sources"],
                "difficulty": q_data["difficulty"],
                "metrics": eval_result["metrics"],
                "overall_score": eval_result["overall_score"]
            }
            
            results["questions_evaluated"].append(q_result)
            
            # Aggregate scores
            for metric_name, metric_data in eval_result["metrics"].items():
                if "score" in metric_data:
                    results["aggregate_scores"][metric_name].append(metric_data["score"])
            results["aggregate_scores"]["overall"].append(eval_result["overall_score"])
            
            print(f"   ✓ Overall Score: {eval_result['overall_score']:.2f}")
            print(f"   - Faithfulness: {eval_result['metrics']['faithfulness']['score']:.2f}")
            print(f"   - Relevance: {eval_result['metrics']['relevance']['score']:.2f}")
            print(f"   - Citation: {eval_result['metrics']['citation_accuracy']['score']:.2f}")
            
        except Exception as e:
            print(f"   ✗ Error: {e}")
            results["questions_evaluated"].append({
                "id": q_data["id"],
                "question": q_data["question"],
                "error": str(e)
            })
    
    # Calculate averages
    results["avg_scores"] = {
        metric: sum(scores) / len(scores) if scores else 0.0
        for metric, scores in results["aggregate_scores"].items()
    }
    
    # Save report
    report_dir = Path("evaluation_reports")
    report_dir.mkdir(exist_ok=True)
    
    report_file = report_dir / f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Total Questions: {results['total_questions']}")
    print(f"Successfully Evaluated: {len([q for q in results['questions_evaluated'] if 'error' not in q])}")
    print(f"\nAverage Scores:")
    print(f"  Faithfulness:      {results['avg_scores'].get('faithfulness', 0):.2%}")
    print(f"  Relevance:         {results['avg_scores'].get('relevance', 0):.2%}")
    print(f"  Citation Accuracy: {results['avg_scores'].get('citation_accuracy', 0):.2%}")
    print(f"  Overall Score:     {results['avg_scores'].get('overall', 0):.2%}")
    print(f"\nReport saved to: {report_file}")
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run RAG system evaluation")
    parser.add_argument("--sample-size", type=int, default=5, 
                       help="Number of questions to evaluate (default: 5)")
    
    args = parser.parse_args()
    
    run_evaluation(sample_size=args.sample_size)
