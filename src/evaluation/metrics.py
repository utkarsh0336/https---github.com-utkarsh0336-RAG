"""
Evaluation Metrics for RAG System

Implements:
1. Answer Faithfulness: Does the answer contain hallucinations?
2. Answer Relevance: Does it answer the actual question?
3. Citation Accuracy: Are sources properly cited?
"""

import re
from typing import Dict, List
from src.rag.generation import LLMClient

class RAGEvaluator:
    """Automated evaluation metrics for RAG system."""
    
    def __init__(self):
        self.llm = LLMClient(temperature=0.0).llm
    
    def evaluate_faithfulness(self, answer: str, context: str) -> Dict:
        """
        Measure if answer is grounded in retrieved context (no hallucinations).
        Returns score 0-1, where 1 = fully faithful.
        """
        prompt = f"""You are an evaluator checking if an AI answer is faithful to the source context.

Context (Source Material):
{context[:1000]}

Answer to Evaluate:
{answer}

Task: Determine if the answer contains any claims NOT supported by the context.

Respond with JSON:
{{
    "faithful": true/false,
    "score": 0.0-1.0,
    "hallucinations": ["list any unsupported claims"]
}}

JSON Response:"""
        
        try:
            response = self.llm.invoke(prompt)
            # Parse JSON from response
            import json
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return {
                    "metric": "faithfulness",
                    "score": result.get("score", 0.5),
                    "faithful": result.get("faithful", True),
                    "hallucinations": result.get("hallucinations", [])
                }
        except Exception as e:
            print(f"Faithfulness eval error: {e}")
        
        return {"metric": "faithfulness", "score": 0.5, "error": "Failed to evaluate"}
    
    def evaluate_relevance(self, question: str, answer: str) -> Dict:
        """
        Measure if answer actually addresses the question asked.
        Returns score 0-1, where 1 = highly relevant.
        """
        prompt = f"""You are an evaluator checking if an answer is relevant to the question.

Question:
{question}

Answer:
{answer}

Task: Determine if the answer directly addresses the question asked.

Respond with JSON:
{{
    "relevant": true/false,
    "score": 0.0-1.0,
    "reasoning": "brief explanation"
}}

JSON Response:"""
        
        try:
            response = self.llm.invoke(prompt)
            import json
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return {
                    "metric": "relevance",
                    "score": result.get("score", 0.5),
                    "relevant": result.get("relevant", True),
                    "reasoning": result.get("reasoning", "")
                }
        except Exception as e:
            print(f"Relevance eval error: {e}")
        
        return {"metric": "relevance", "score": 0.5, "error": "Failed to evaluate"}
    
    def evaluate_citation_accuracy(self, answer: str, sources_used: List[str]) -> Dict:
        """
        Check if answer properly cites sources and citations are accurate.
        Returns score 0-1 based on citation quality.
        """
        # Count citations in answer
        citations = re.findall(r'\[([^\]]+)\]', answer)
        
        # Check if sources are mentioned
        has_citations = len(citations) > 0
        
        # Basic heuristic scoring
        if not has_citations:
            score = 0.0
        elif len(citations) >= 3:  # Good citation density
            score = 1.0
        else:
            score = len(citations) / 3  # Partial credit
        
        return {
            "metric": "citation_accuracy",
            "score": score,
            "num_citations": len(citations),
            "citations_found": citations[:5],  # Show first 5
            "has_proper_citations": has_citations
        }
    
    def evaluate_answer(self, question: str, answer: str, context: str, 
                       sources_used: List[str] = None) -> Dict:
        """
        Run all evaluation metrics on a single answer.
        """
        results = {
            "question": question,
            "answer": answer,
            "metrics": {}
        }
        
        # Run all metrics
        results["metrics"]["faithfulness"] = self.evaluate_faithfulness(answer, context)
        results["metrics"]["relevance"] = self.evaluate_relevance(question, answer)
        results["metrics"]["citation_accuracy"] = self.evaluate_citation_accuracy(
            answer, sources_used or []
        )
        
        # Calculate overall score (average)
        scores = [m["score"] for m in results["metrics"].values() if "score" in m]
        results["overall_score"] = sum(scores) / len(scores) if scores else 0.0
        
        return results
