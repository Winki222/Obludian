from llama_cpp import Llama
import requests
import re

import ollama
class LLM:
    def __init__(self,config):
        self.backend=config["llm"]["backend"]
        self.max_token=config["llm"]["max_tokens"]
        self.temperature=config["llm"]["temperature"]
        if self.backend == "ollama":
            self.model=config["llm"]["model"]
            self.ollama_url=config["llm"]["ollama_url"]
            try:
                requests.get(self.ollama_url)
            except:
                print("Ошибка: запусти ollama serve в терминале")
        elif self.backend == "llamacpp":
            self.llm = Llama(
                model_path=config["llm"]["gguf_path"],
                n_ctx=8192,
                verbose=False)
    
    def ask(self,question, context_chunks):
        context = ""
        for chunk in context_chunks[:3]:
            context += f"\n[{chunk['filename']}]\n{chunk['text']}\n"
        if self.backend=="ollama":
            response= ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content":"Ты помощник по заметкам. Отвечай только на основе контекста. Отвечай на русском языке."},  # роль модели
                    {"role": "user", "content": f"Контекст:\n{context}\n\nВопрос: {question}"} 
                ],
                options={
                    "temperature": self.temperature,
                    "num_predict": self.max_token
                }
            )
            return response["message"]["content"] 
        elif self.backend=="llamacpp":
            response = self.llm.create_chat_completion(
                messages=[
                    {"role": "system", "content": "Ты помощник по заметкам. Отвечай только на основе контекста. Отвечай на русском языке."}, 
                    {"role": "user", "content": f"Контекст:\n{context}\n\nВопрос: {question}"}
                ],
                
                max_tokens=self.max_token,    
                temperature=self.temperature
            )
            text = response["choices"][0]["message"]["content"]
        text = response["choices"][0]["message"]["content"]
        
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
        return text