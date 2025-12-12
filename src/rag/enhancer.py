import os
import numpy as np
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import faiss
import google.generativeai as genai
from dotenv import load_dotenv

# Load .env safely
load_dotenv()

print("📦 Loading embedding model...")
embed_model = SentenceTransformer('all-MiniLM-L6-v2')
print("✅ Embedding model loaded.")

class SimpleVectorStore:
    def __init__(self, texts: List[str]):
        self.texts = texts
        embeddings = embed_model.encode(texts)
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(np.array(embeddings, dtype=np.float32))
    
    def similarity_search(self, query: str, k: int = 2) -> List[str]:
        query_vec = embed_model.encode([query])
        query_vec = np.array(query_vec, dtype=np.float32)
        distances, indices = self.index.search(query_vec, k)
        return [self.texts[i] for i in indices[0]]

def enhance_summaries(projects: List[Dict]) -> List[Dict]:
    # Configure Gemini
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not found in environment")
    genai.configure(api_key=api_key)
    llm = genai.GenerativeModel('gemini-2.0-flash-001')

    summaries = [p["summary"] for p in projects if p.get("summary")]
    if not summaries:
        return projects

    # Build vector store from all project summaries
    print("🧠 Building vector store...")
    vectorstore = SimpleVectorStore(summaries)
    print("✅ Vector store ready.")

    enhanced = []
    for proj in projects:
        summary = proj.get("summary", "").strip()
        if not summary:
            enhanced.append(proj)
            continue

        # Retrieve similar summaries (for RAG context)
        similar = vectorstore.similarity_search(summary, k=2)
        context = "\n".join(similar)

        prompt = f"""You are a professional technical writer enhancing a DevOps/AI engineer's portfolio.
Use this context from their other projects to maintain consistency:
{context}

Now, improve this project summary to be concise, impactful, and highlight AWS, DevOps, Python, or AI/LLM technologies:
"{summary}"

Return ONLY the improved 1–2 sentence summary. No markdown, no extra text."""

        try:
            print(f"✨ Enhancing: {proj['title']}")
            response = llm.generate_content(prompt)
            # Clean response (sometimes has leading/trailing whitespace or quotes)
            enhanced_text = response.text.strip().strip('"').strip("'")
            proj["enhanced_summary"] = enhanced_text
        except Exception as e:
            print(f"⚠️ Error enhancing '{proj['title']}': {e}")
            proj["enhanced_summary"] = summary  # fallback

        enhanced.append(proj)

    return enhanced