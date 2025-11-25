import wikipedia
import uuid
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sentence_transformers import SentenceTransformer
from src.rag.qdrant_handler import QdrantHandler
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Configuration
COLLECTION_NAME = "wiki_rag"
ROOT_ARTICLE = "Generative pre-trained transformer"
MAX_DEPTH = 1  # 0 = only root, 1 = root + direct links
MAX_PAGES = 20 # Limit to avoid taking forever

def get_wiki_content(title):
    try:
        page = wikipedia.page(title, auto_suggest=False)
        return page.content, page.links
    except Exception as e:
        print(f"Error fetching {title}: {e}")
        return None, []

def ingest_wiki():
    print("Initializing Qdrant and Model...")
    qdrant = QdrantHandler()
    qdrant.create_collection(COLLECTION_NAME, vector_size=384)
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

    visited = set()
    queue = [(ROOT_ARTICLE, 0)]
    
    documents = []
    metadatas = []
    
    print(f"Starting crawl from '{ROOT_ARTICLE}'...")
    
    while queue and len(visited) < MAX_PAGES:
        title, depth = queue.pop(0)
        if title in visited:
            continue
        
        visited.add(title)
        print(f"Processing: {title} (Depth {depth})")
        
        content, links = get_wiki_content(title)
        if not content:
            continue
            
        # Chunking
        chunks = text_splitter.split_text(content)
        for chunk in chunks:
            documents.append(chunk)
            metadatas.append({"source": "wikipedia", "title": title, "url": f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"})
            
        if depth < MAX_DEPTH:
            for link in links:
                if link not in visited:
                    queue.append((link, depth + 1))
    
    print(f"Embedding {len(documents)} chunks...")
    embeddings = model.encode(documents).tolist()
    
    print("Uploading to Qdrant...")
    # Upload in batches of 100
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        end = min(i + batch_size, len(documents))
        qdrant.add_documents(
            COLLECTION_NAME,
            documents[i:end],
            metadatas[i:end],
            embeddings[i:end]
        )
    
    print("Ingestion complete!")

if __name__ == "__main__":
    ingest_wiki()
