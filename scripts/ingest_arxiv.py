import arxiv
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sentence_transformers import SentenceTransformer
from src.rag.qdrant_handler import QdrantHandler
from langchain_text_splitters import RecursiveCharacterTextSplitter

COLLECTION_NAME = "arxiv_rag"
MAX_PAPERS = 50

def ingest_arxiv():
    print("Initializing Qdrant and Model...")
    qdrant = QdrantHandler()
    qdrant.create_collection(COLLECTION_NAME, vector_size=384)
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    
    client = arxiv.Client()
    search = arxiv.Search(
        query="cat:cs.CL OR cat:cs.LG",
        max_results=MAX_PAPERS,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    
    documents = []
    metadatas = []
    
    print(f"Fetching {MAX_PAPERS} papers from ArXiv...")
    for result in client.results(search):
        text = f"Title: {result.title}\nAbstract: {result.summary}"
        chunks = text_splitter.split_text(text)
        
        for chunk in chunks:
            documents.append(chunk)
            metadatas.append({
                "source": "arxiv",
                "title": result.title,
                "url": result.entry_id,
                "published": str(result.published)
            })
            
    print(f"Embedding {len(documents)} chunks...")
    embeddings = model.encode(documents).tolist()
    
    print("Uploading to Qdrant...")
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        end = min(i + batch_size, len(documents))
        qdrant.add_documents(
            COLLECTION_NAME,
            documents[i:end],
            metadatas[i:end],
            embeddings[i:end]
        )
        
    print("ArXiv Ingestion complete!")

if __name__ == "__main__":
    ingest_arxiv()
