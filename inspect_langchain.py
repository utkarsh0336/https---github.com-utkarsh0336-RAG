import langchain.agents
import inspect

print(f"langchain.agents dir: {dir(langchain.agents)}")

try:
    from langchain.agents import AgentExecutor
    print("AgentExecutor found in langchain.agents")
except ImportError:
    print("AgentExecutor NOT found in langchain.agents")
    
try:
    from langchain.agents.agent import AgentExecutor
    print("AgentExecutor found in langchain.agents.agent")
except ImportError:
    print("AgentExecutor NOT found in langchain.agents.agent")
