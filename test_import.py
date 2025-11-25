try:
    from langchain.agents.agent_executor import AgentExecutor
    print("Found in langchain.agents.agent_executor")
except ImportError as e:
    print(f"Failed agent_executor: {e}")

try:
    from langchain.agents import AgentExecutor
    print("Found in langchain.agents")
except ImportError as e:
    print(f"Failed agents: {e}")
