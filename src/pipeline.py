from langchain_ollama import ChatOllama, OllamaEmbeddings
from langgraph.graph.state import CompiledStateGraph

from configs.config import Settings, get_settings
from src.graph import build_graph
from src.ingestion import build_retriever
from src.nodes import PipelineNodes
from src.schemas import QueryResponse, SourceDocument
from src.state import RAGState


class QueryPlanningPipeline:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        llm = ChatOllama(
            model=self.settings.ollama_chat_model,
            temperature=self.settings.ollama_temperature,
            base_url=self.settings.ollama_base_url,
        )
        embeddings = OllamaEmbeddings(
            model=self.settings.ollama_embed_model,
            base_url=self.settings.ollama_base_url,
        )
        retriever = build_retriever(self.settings, embeddings)
        self.graph: CompiledStateGraph = build_graph(PipelineNodes(llm, retriever))

    def invoke(self, question: str) -> RAGState:
        initial_state: RAGState = {
            "question": question,
            "sub_questions": [],
            "retrieved_docs": [],
            "answer": "",
        }
        return self.graph.invoke(initial_state)

    def invoke_response(self, question: str) -> QueryResponse:
        result = self.invoke(question)
        seen: set[str] = set()
        sources: list[SourceDocument] = []
        for doc in result["retrieved_docs"]:
            url = str(doc.metadata.get("source") or "")
            if url in seen:
                continue
            seen.add(url)
            title = str(doc.metadata.get("title") or url or "Untitled source")
            snippet = doc.page_content.strip().replace("\n", " ")
            sources.append(
                SourceDocument(
                    source=url,
                    title=title,
                    snippet=snippet[:320],
                )
            )
        return QueryResponse(
            question=result["question"],
            sub_questions=result["sub_questions"],
            sources=sources,
            answer=result["answer"],
        )
