from core.retriever import Retriever
from core.llm import LLM
from core.indexer import Indexer
from datetime import datetime
from pathlib import Path
import time
import os
class Agent:
    def __init__(self,config):
        self.config=config
        self.retriever= Retriever(config)
        self.llm=LLM(config)
        self.indexer=Indexer(config)
    
    def answer_question(self, question):
        chunks=self.retriever.search(question, top_k=4)
        if not chunks :
            return "ничего не найдено по этой теме"
        response = self.llm.ask(question, chunks)
        sources = set(chunk["filename"] for chunk in chunks)
        return f"{response}\n\nИсточники: {', '.join(sources)}"
    
    def find_connection(self, note_name):
        notes= self.retriever.find_connections(note_name)
        if not notes:
            return "Не нашёл связанных заметок"
        text = "🔗 Связанные заметки:\n"
        for note in notes:
            text += f"• {note['filename']} (схожесть: {round((1 - note['distance']) * 100)}%)\n"
        return text
    
    def create_note(self, title,content):
        data_time=datetime.now().strftime('%Y-%m-%d')
        path = Path(self.config["vault_path"]) / self.config["new_notes_folder"] / f"{data_time}_{title}.md"
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {title}\n\n{content}", encoding="utf-8")
        self.indexer.index()
        return str(path)
    def get_stale_notes(self, days):
        metas = self.retriever.collection.get(include=["metadatas"])
        now = datetime.now().timestamp()
        seen = set()     
        stale = []      
        for meta in metas["metadatas"]:
            filename = meta["filename"]
            if filename in seen:
                continue         
            seen.add(filename)
            
            modified = meta.get("modified")  # время изменения
            if modified is None:
                continue
                
            days_ago = (now - modified) / 86400
            if days_ago > days:
                stale.append(meta) 
        if not stale:
            return "Все заметки свежие 👍"
        text = f"📅 Заметки которые ты не трогал {days}+ дней:\n"
        for note in stale:
            days_ago = (now - note["modified"]) / 86400
            text += f"• {note['filename']} ({int(days_ago)} дн. назад)\n"
        return text
        
        # сформировать текст и вернуть
