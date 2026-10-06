import os

os.environ.setdefault("USER_AGENT", "query-planning-decomposition/0.1")

from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_text_splitters import RecursiveCharacterTextSplitter

from configs.config import Settings


def build_retriever(settings: Settings, embeddings: Embeddings) -> VectorStoreRetriever:
    os.environ["USER_AGENT"] = settings.user_agent
    documents = []
    for url in settings.source_urls:
        loader = WebBaseLoader(
            url,
            header_template={"User-Agent": settings.user_agent},
        )
        documents.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    chunks = splitter.split_documents(documents)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    return vectorstore.as_retriever()
