from typing import Dict, List

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.core.config import Settings


class RAGEngine:
    def __init__(self, config: Settings):
        self.config = config
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.config.EMBEDDINGS_MODEL,
            model_kwargs={"device": "cpu"},
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.CHUNK_SIZE,
            chunk_overlap=self.config.CHUNK_OVERLAP,
        )

    def create_vector_db(self, classified_chunks: List[Dict]) -> FAISS:
        """Создает базу данных, учитывая категории и заголовки"""
        docs = []
        for item in classified_chunks:
            header_prefix = (
                f"Раздел: {item['category']} | Заголовок: {item['title']}\n"
            )

            sub_chunks = self.text_splitter.split_text(item["text"])

            for chunk in sub_chunks:
                docs.append(
                    Document(
                        page_content=header_prefix + chunk,
                        metadata={
                            "category": item["category"],
                            "title": item["title"],
                            "original_header": item.get("original", ""),
                        },
                    )
                )

        return FAISS.from_documents(docs, self.embeddings)

    def retrieve_relevant_chunks(
        self,
        vector_db: FAISS,
        query: str,
        k: int = None,
        categories: List[str] = None,
    ) -> List[Document]:
        """Извлекает чанки с опциональной фильтрацией по категориям"""
        if k is None:
            k = self.config.K_RETRIEVALS

        search_kwargs = {}
        if categories:
            search_kwargs["filter"] = (
                lambda meta: meta.get("category") in categories
            )

        return vector_db.similarity_search(query, k=k, **search_kwargs)

    def get_context_from_docs(self, docs: List[Document]) -> str:
        return "\n---\n".join(
            [f"[{d.metadata['title']}]: {d.page_content}" for d in docs]
        )
