PLANNER_PROMPT = """Break the following complex question into 2-3 focused sub-questions.
Return only the sub-questions, one per line, with no numbering or extra commentary.

Question: {question}
"""

ANSWER_PROMPT = """Use the retrieved context to answer the question.
Be complete and precise. If the context is insufficient, say so.

Context:
{context}

Question: {question}
"""
