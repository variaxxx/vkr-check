from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List
import config

class RAGEngine:
    """Универсальный RAG движок для работы с векторными базами данных"""
    
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=config.Config.EMBEDDINGS_MODEL
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.Config.CHUNK_SIZE,
            chunk_overlap=config.Config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def create_vector_db(self, text: str) -> FAISS:
        """Создает векторную базу данных из текста"""
        chunks = self.text_splitter.split_text(text)
        docs = [Document(page_content=chunk) for chunk in chunks]
        return FAISS.from_documents(docs, self.embeddings)
    
    def retrieve_relevant_chunks(self, vector_db: FAISS, query: str, k: int = None) -> List[Document]:
        """Извлекает релевантные фрагменты из векторной БД"""
        if k is None:
            k = config.Config.K_RETRIEVALS
        return vector_db.similarity_search(query, k=k)
    
    def get_context_from_docs(self, docs: List[Document]) -> str:
        """Форматирует документы в строку контекста"""
        return "\n---\n".join([d.page_content for d in docs])