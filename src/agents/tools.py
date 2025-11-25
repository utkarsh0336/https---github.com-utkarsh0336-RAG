import os
import sqlite3
import arxiv
from typing import List, Dict
from langchain_core.tools import tool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.tools import TavilySearchResults
from duckduckgo_search import DDGS
from langdetect import detect, LangDetectException

# Web Search Tool
@tool
def web_search_tool(query: str) -> str:
    """Performs a web search to find recent information."""
    try:
        # Prefer Tavily if available, else Serper, else DuckDuckGo (Free)
        if os.getenv("TAVILY_API_KEY"):
            tool = TavilySearchResults(max_results=3)
            results = tool.invoke({"query": query})
            return str(results)
        elif os.getenv("SERPER_API_KEY"):
            search = GoogleSerperAPIWrapper()
            return search.run(query)
        else:
            # Fallback to free DuckDuckGo search using direct library with retry logic
            with DDGS() as ddgs:
                for backend in ["html", "lite", "api"]:
                    try:
                        results = list(ddgs.text(query, max_results=10, backend=backend))
                        if results:
                            # Filter for English-only results
                            english_results = []
                            for r in results:
                                try:
                                    # Check if title or body is in English
                                    text = r.get('title', '') + ' ' + r.get('body', '')
                                    if detect(text) == 'en':
                                        english_results.append(r)
                                        if len(english_results) >= 3:
                                            break
                                except LangDetectException:
                                    # If detection fails, include it anyway
                                    english_results.append(r)
                                    if len(english_results) >= 3:
                                        break
                            
                            if english_results:
                                return str(english_results)
                    except Exception:
                        continue
                
                return "No results found."
    except Exception as e:
        return f"Search failed: {e}"

# SQL Tool
@tool
def sql_query_tool(query: str) -> str:
    """Executes a SQL query against the ai_models.db database. 
    The table is 'models' with columns: model_name, release_year, parameter_count, organization, sota_benchmark.
    """
    db_path = "data/ai_models.db"
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        conn.close()
        
        if not results:
            return "No results found."
        
        formatted_results = []
        for row in results:
            formatted_results.append(dict(zip(columns, row)))
            
        return str(formatted_results)
    except Exception as e:
        return f"SQL Error: {e}"

# ArXiv Tool
@tool
def arxiv_search_tool(query: str) -> str:
    """Searches ArXiv for research papers."""
    try:
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=3,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        results = []
        for r in client.results(search):
            results.append(f"Title: {r.title}\nSummary: {r.summary}\nPublished: {r.published}")
            
        return "\n---\n".join(results)
    except Exception as e:
        return f"ArXiv search failed: {e}"
