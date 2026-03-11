import os
from functools import lru_cache
from sentence_transformers import SentenceTransformer
from core.config import load_config

os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

@lru_cache(maxsize=1)  # ← кэшируем модель навсегда в памяти
def get_embedder():
    cfg = load_config()
    print(" Загрузка эмбеддинг-модели... (только один раз!)")
    return SentenceTransformer(cfg["embeddings"]["model"])