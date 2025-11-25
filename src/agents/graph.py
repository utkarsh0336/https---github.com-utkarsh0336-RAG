from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from src.rag.retrieval import MultiSourceRetriever
from src.rag.generation import AnswerGenerator
from src.agents.validation import ValidationAgent, ValidationReport
from src.agents.execution import ExecutionAgent
from src.agents.synthesis import SynthesisAgent
from src.cache import RedisCache
from src.observability import get_tracker

class GraphState(TypedDict):
    question: str
    context: str
    initial_answer: str
    validation_report: dict
    new_info: str
    final_answer: str

class RAGGraph:
    def __init__(self):
        self.retriever = MultiSourceRetriever()
        self.generator = AnswerGenerator()
        self.validator = ValidationAgent()
        self.executor = ExecutionAgent()
        self.synthesizer = SynthesisAgent()
        
        # Initialize cache
        try:
            self.cache = RedisCache()
        except Exception as e:
            print(f"Redis cache not available: {e}")
            self.cache = None
        
        self.workflow = StateGraph(GraphState)
        
        # Define Nodes
        self.workflow.add_node("retrieve", self.retrieve_node)
        self.workflow.add_node("generate", self.generate_node)
        self.workflow.add_node("validate", self.validate_node)
        self.workflow.add_node("execute", self.execute_node)
        self.workflow.add_node("synthesize", self.synthesize_node)
        
        # Define Edges
        self.workflow.set_entry_point("retrieve")
        self.workflow.add_edge("retrieve", "generate")
        self.workflow.add_edge("generate", "validate")
        
        # Conditional Edge
        self.workflow.add_conditional_edges(
            "validate",
            self.check_validation,
            {
                "accepted": END,
                "needs_work": "execute"
            }
        )
        
        self.workflow.add_edge("execute", "synthesize")
        self.workflow.add_edge("synthesize", END)
        
        self.app = self.workflow.compile()
        
    def retrieve_node(self, state: GraphState):
        print("---RETRIEVE---")
        docs = self.retriever.retrieve(state["question"])
        context = "\n\n".join([d.page_content for d in docs])
        
        # Log retrieval
        tracker = get_tracker()
        tracker.log_retrieval("multi_source", state["question"], 
                            [{"page_content": d.page_content, "metadata": d.metadata} for d in docs])
        
        return {"context": context}
    
    def generate_node(self, state: GraphState):
        print("---GENERATE---")
        answer = self.generator.generate(state["question"], state["context"])
        
        # Log generation
        tracker = get_tracker()
        tracker.log_generation(answer)
        
        return {"initial_answer": answer}
    
    def validate_node(self, state: GraphState):
        print("---VALIDATE---")
        report = self.validator.validate(state["question"], state["context"], state["initial_answer"])
        # Ensure report is dict
        if hasattr(report, "dict"):
            report = report.dict()
        
        # Log validation
        tracker = get_tracker()
        tracker.log_validation(report)
        
        # Set final_answer here if validation passes (will be used by conditional logic)
        result = {"validation_report": report}
        
        # If answer is complete and not outdated, set final_answer now
        if (report.get("is_complete", False) and 
            not report.get("is_outdated", False) and 
            report.get("score", 0) > 0.8):
            result["final_answer"] = state["initial_answer"]
            
        return result
    
    def check_validation(self, state: GraphState):
        print("---CHECK VALIDATION---")
        report = state["validation_report"]
        
        # If outdated, force execution regardless of score
        if report.get("is_outdated", False):
            print("Answer is outdated. Fetching new info...")
            return "needs_work"
            
        if report.get("is_complete", False) and report.get("score", 0) > 0.8:
            # final_answer already set in validate_node
            return "accepted"
        return "needs_work"
    
    def execute_node(self, state: GraphState):
        print("---EXECUTE---")
        report = state["validation_report"]
        gaps = report.get("gaps", [])
        queries = report.get("search_queries", [])
        new_info = self.executor.execute_plan(gaps, queries)
        return {"new_info": new_info}
    
    def synthesize_node(self, state: GraphState):
        print("---SYNTHESIZE---")
        final = self.synthesizer.synthesize(
            state["question"],
            state["initial_answer"],
            str(state["validation_report"]),
            state["new_info"]
        )
        
        # Log synthesis
        tracker = get_tracker()
        sources = []
        if state.get("context"): sources.append("VectorDB")
        if state.get("new_info"): sources.append("Web/ArXiv/SQL")
        tracker.log_synthesis(final, sources)
        
        return {"final_answer": final}
        
    def run(self, question: str):
        # Start tracking
        tracker = get_tracker()
        run_id = tracker.start_run(question)
        
        try:
            # Check Tier 1 cache for exact query match
            if self.cache:
                cached_answer = self.cache.get_answer(question)
                if cached_answer:
                    print(f"Cache hit: answer for '{question[:30]}...'")
                    tracker.log_cache_hit(cached_answer)
                    tracker.end_run()
                    return {"final_answer": cached_answer, "question": question}
            
            # Execute the graph
            inputs = {"question": question}
            result = self.app.invoke(inputs)
            
            # Cache the final answer (Tier 1)
            if self.cache and "final_answer" in result:
                # Use shorter TTL if answer includes web-sourced info
                has_web_info = "new_info" in result and result.get("new_info")
                if has_web_info:
                    self.cache.set_web_answer(question, result["final_answer"])
                else:
                    self.cache.set_answer(question, result["final_answer"])
            
            # End tracking and save log
            tracker.end_run()
            
            return result
        except Exception as e:
            tracker.end_run()
            raise e
