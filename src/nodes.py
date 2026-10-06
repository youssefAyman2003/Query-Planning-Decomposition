import re

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.vectorstores import VectorStoreRetriever

from src.prompts import ANSWER_PROMPT, PLANNER_PROMPT
from src.state import RAGState


def parse_sub_questions(raw: str) -> list[str]:
    questions: list[str] = []
    for line in raw.strip().splitlines():
        cleaned = line.strip().lstrip("-•*").strip()
        cleaned = re.sub(r"^\d+[\.\)]\s*", "", cleaned)
        if cleaned:
            questions.append(cleaned)
    return questions


class PipelineNodes:
    def __init__(self, llm: BaseChatModel, retriever: VectorStoreRetriever) -> None:
        self.llm = llm
        self.retriever = retriever

    def plan_query(self, state: RAGState) -> dict:
        prompt = PLANNER_PROMPT.format(question=state["question"])
        result = self.llm.invoke(prompt)
        content = result.content if isinstance(result.content, str) else str(result.content)
        return {"sub_questions": parse_sub_questions(content)}

    def retrieve_for_each(self, state: RAGState) -> dict:
        all_docs = []
        for sub_question in state["sub_questions"]:
            all_docs.extend(self.retriever.invoke(sub_question))
        return {"retrieved_docs": all_docs}

    def generate_final_answer(self, state: RAGState) -> dict:
        context = "\n\n".join(doc.page_content for doc in state["retrieved_docs"])
        prompt = ANSWER_PROMPT.format(context=context, question=state["question"])
        answer = self.llm.invoke(prompt).content
        if not isinstance(answer, str):
            answer = str(answer)
        return {"answer": answer}
