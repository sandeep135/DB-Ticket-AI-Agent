from langgraph.prebuilt import create_react_agent
from app.models import llm
from app.tools import tools

graph = create_react_agent(llm, tools=tools)
