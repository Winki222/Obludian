import chromadb
from pathlib import Path
from core.embeddings import get_embedder

class Retriever:
    def __init__(self, config):
        self.config = config
        self.embedder = get_embedder()    
        self.client = chromadb.PersistentClient(path="./db")
        self.collection = self.client.get_or_create_collection(name="notes")
    def search(self, query: str, top_k: int = 5):
        query_emb = self.embedder.encode([query])[0]

        results = self.collection.query(
            query_embeddings=[query_emb],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        items = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ):
            if dist > 0.8:
                continue
            items.append({
                "text": doc,
                "filename": meta["filename"],
                "path": meta["path"],
                "distance": dist
            })
        return items

    def find_connections(self, note_name: str, top_k: int = 3):
        data = self.collection.get(where={"filename": note_name})
        if not data["documents"]:
            return []
        short = " ".join(data["documents"][:3])[:1000]
        results = self.search(short, top_k=10)

        seen = set()
        unique = []
        for r in results:
            if r["filename"] != note_name and r["filename"] not in seen:
                seen.add(r["filename"])
                unique.append(r)
                if len(unique) >= top_k:
                    break
        return unique

    def get_stale_notes(self, days: int):
        data = self.collection.get(include=["metadatas"])
        stale = []
        now = __import__('datetime').datetime.now().timestamp()
        seen = set()
        for meta in data.get("metadatas", []):
            fn = meta.get("filename")
            if fn in seen or not fn:
                continue
            seen.add(fn)
            age = (now - meta.get("modified_time", 0)) / 86400
            if age > days and not any(skip in meta.get("path", "") for skip in self.config["skip_folders"]):
                stale.append({
                    "filename": fn,
                    "path": meta.get("path", ""),
                    "days_ago": int(age)
                })
        return sorted(stale, key=lambda x: x["days_ago"], reverse=True)