from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.rag.generation import LLMClient

class SynthesisAgent:
    def __init__(self):
        self.llm = LLMClient(temperature=0.7).llm
        
        self.prompt = ChatPromptTemplate.from_template("""
        You are the final synthesizer in a RAG pipeline. Your task is to create a comprehensive, well-cited answer.
        
        Original Question: {question}
        
        Initial Answer (from Primary VectorDB - Wikipedia/ArXiv): {initial_answer}
        
        Validation Issues: {validation_report}
        
        New Information Found (from Web Search, ArXiv API, SQL Database): {new_info}
        
        Your task:
        1. Synthesize a FINAL, comprehensive answer that addresses the original question.
        2. Incorporate ALL relevant information from multiple sources:
           - Primary VectorDB (Wikipedia/ArXiv embeddings)
           - Web Search results
           - ArXiv research papers (via API)
           - SQL database queries
        3. Resolve any conflicts between sources by:
           - Prioritizing recent web/paper info over old data
           - Noting when sources disagree
           - Explaining which source is more credible and why
        4. Provide INLINE CITATIONS for every key claim in this format:
           - [VectorDB: Wikipedia] for information from the primary vector database
           - [Web: URL] for web search results
           - [ArXiv: Paper Title] for ArXiv papers
           - [Database: Table/Query] for SQL database results
        5. Write in a conversational, helpful tone.
        6. If information is contradictory, explain the contradiction and state which source is likely more reliable.
        
        IMPORTANT: Every factual claim must have a citation. Use the format shown above.
        
        Final Answer:
        """)
        
        self.chain = self.prompt | self.llm | StrOutputParser()
        
    def synthesize(self, question: str, initial_answer: str, validation_report: str, new_info: str) -> str:
        return self.chain.invoke({
            "question": question,
            "initial_answer": initial_answer,
            "validation_report": validation_report,
            "new_info": new_info
        })
