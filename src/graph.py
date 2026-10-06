from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from src.nodes import PipelineNodes
from src.state import RAGState


def build_graph(nodes: PipelineNodes) -> CompiledStateGraph:
    builder = StateGraph(RAGState)
    builder.add_node("planner", nodes.plan_query)
    builder.add_node("retriever", nodes.retrieve_for_each)
    builder.add_node("responder", nodes.generate_final_answer)

    builder.add_edge(START, "planner")
    builder.add_edge("planner", "retriever")
    builder.add_edge("retriever", "responder")
    builder.add_edge("responder", END)
    return builder.compile()
