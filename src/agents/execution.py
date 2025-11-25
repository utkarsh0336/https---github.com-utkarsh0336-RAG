from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.rag.generation import LLMClient
from src.agents.tools import web_search_tool, sql_query_tool, arxiv_search_tool

class ExecutionAgent:
    def __init__(self):
        self.llm = LLMClient(model_name="gemini-2.0-flash").llm 
        self.tools = {
            "web_search": web_search_tool,
            "sql_query": sql_query_tool,
            "arxiv_search": arxiv_search_tool
        }
        
        self.prompt = ChatPromptTemplate.from_template("""
        You are an advanced research assistant. Your goal is to gather information to answer specific questions.
        
        The user has identified gaps in a previous answer:
        Gaps to fill: {gaps}
        Suggested queries: {queries}
        
        Based on these gaps, I will now search for information using available tools.
        Please provide a summary of what needs to be found.
        """)
        
        self.chain = self.prompt | self.llm | StrOutputParser()
        
    def execute_plan(self, gaps: list, queries: list) -> str:
        try:
            # Get LLM's analysis
            analysis = self.chain.invoke({
                "gaps": ", ".join(gaps),
                "queries": ", ".join(queries)
            })
            
            # Execute tools based on queries
            results = []
            for query in queries[:3]:  # Limit to 3 queries
                # Try web search first
                try:
                    web_result = self.tools["web_search"].invoke(query)
                    results.append(f"Web Search for '{query}':\n{web_result}")
                except Exception as e:
                    results.append(f"Web search failed: {e}")
                    
            return "\n\n".join(results) if results else "No additional information found."
        except Exception as e:
            return f"Execution failed: {e}"
