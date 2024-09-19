from langchain_core.runnables import RunnableLambda
from app.agents import graph

def inp(question:str):
    return {"messages": question}

def out(state:dict):
    return state["messages"][-1].content

full_chain = RunnableLambda(inp)|graph|RunnableLambda(out)


