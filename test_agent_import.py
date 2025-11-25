try:
    from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
    print("✓ AgentExecutor imported successfully from langchain_classic")
except ImportError as e:
    print(f"✗ Import failed: {e}")
