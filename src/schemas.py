from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(min_length=8, max_length=4000)


class SourceDocument(BaseModel):
    source: str
    title: str
    snippet: str


class QueryResponse(BaseModel):
    question: str
    sub_questions: list[str]
    sources: list[SourceDocument]
    answer: str


class StatusResponse(BaseModel):
    ready: bool
    error: str | None = None
