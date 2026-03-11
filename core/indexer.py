import hashlib
import os
from pathlib import Path
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from core.embeddings import get_embedder  

class Indexer:
    def __init__(self, config: dict):
        self.config = config
        self.vault_path = Path(config["vault_path"])
        self.skip_folders = config["skip_folders"]
        self.chunk_size = config["indexer"]["chunk_size"]
        self.chunk_overlap = config["indexer"]["chunk_overlap"]
        self.embedder = get_embedder()
        
        self.client = chromadb.PersistentClient(path="./db")
        self.collection = self.client.get_or_create_collection(name="notes")

    def _load_notes(self):
        notes_list = []
        for note in self.vault_path.rglob("*.md"):
            if any(folder in note.parts for folder in self.skip_folders):
                continue
            try:
                text = note.read_text(encoding="utf-8", errors="ignore")
                notes_list.append({
                    "text": text,
                    "filename": note.name,
                    "path": str(note),
                    "modified_time": os.path.getmtime(note)
                })
            except Exception as e:
                print(f"⚠️ Пропущен файл {note}: {e}")
        return notes_list

    def _chunk_text(self, text: str):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        return splitter.split_text(text)

    def _get_cached_hashes(self):
        result = self.collection.get(include=["metadatas"])
        cached = {}
        for meta in result.get("metadatas", []):
            if meta and "filename" in meta and "file_hash" in meta:
                cached[meta["filename"]] = meta["file_hash"]
        return cached

    def index(self):
        notes = self._load_notes()
        cached = self._get_cached_hashes()
        processed = 0

        for note in notes:
            file_hash = hashlib.md5(note["text"].encode()).hexdigest()
            if cached.get(note["filename"]) == file_hash:
                continue
            self.collection.delete(where={"filename": note["filename"]})
            chunks = self._chunk_text(note["text"])
            if not chunks:
                continue

            all_ids = []
            all_chunks = []
            all_metadatas = []

            for i, chunk in enumerate(chunks):
                all_ids.append(f"{note['filename']}__chunk_{i}")
                all_chunks.append(chunk)
                all_metadatas.append({
                    "filename": note["filename"],
                    "path": note["path"],
                    "modified_time": note["modified_time"],
                    "file_hash": file_hash,
                    "chunk_index": i
                })
            embeddings = self.embedder.encode(all_chunks, batch_size=8)

            self.collection.add(
                documents=all_chunks,
                embeddings=embeddings.tolist(),  # ChromaDB требует list
                ids=all_ids,
                metadatas=all_metadatas
            )
            processed += 1

        if processed == 0:
            print("Всё уже проиндексировано (нет изменений)")
        else:
            print(f" Проиндексировано {processed} новых/изменённых файлов")