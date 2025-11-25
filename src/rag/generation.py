import os
import google.generativeai as genai
from langchain_core.runnables import RunnableSerializable
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import Any, Dict

class SimpleLLM(RunnableSerializable):
    """Simple wrapper for Google Gemini that works with LangChain."""
    
    model_name: str = "gemini-2.0-flash"
    temperature: float = 0.0
    _model: Any = None
    
    def __init__(self, model_name: str = "gemini-2.0-flash", temperature: float = 0.0, **kwargs):
        super().__init__(model_name=model_name, temperature=temperature, **kwargs)
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not set")
        
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(model_name)
    
    def invoke(self, input_data: Any, config: Dict = None) -> str:
        """Handle invoke from LangChain chains."""
        # Extract the actual prompt text
        if isinstance(input_data, str):
            prompt = input_data
        elif isinstance(input_data, dict):
            # Convert dict to string representation
            prompt = str(input_data)
        else:
            prompt = str(input_data)
        
        response = self._model.generate_content(prompt)
        return response.text

class LLMClient:
    def __init__(self, model_name: str = "gemini-2.0-flash", temperature: float = 0.7):
        self.llm = SimpleLLM(model_name=model_name, temperature=temperature)

class AnswerGenerator:
    def __init__(self):
        self.llm_client = LLMClient()
        self.llm = self.llm_client.llm
        
        self.prompt = ChatPromptTemplate.from_template("""
        You are an expert AI assistant. Answer the user's question based on the provided context.
        If the context does not contain enough information to answer the question fully, state what information is available and what is missing.
        
        Provide a clear, natural answer without citations or source references.
        
        Context:
        {context}
        
        Question: {question}
        
        Answer:
        """)
        
        self.chain = self.prompt | self.llm | StrOutputParser()
        
    def generate(self, question: str, context: str) -> str:
        return self.chain.invoke({"question": question, "context": context})

