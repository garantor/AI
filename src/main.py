from langchain.agents import create_openai_functions_agent
from langchain.agents import AgentExecutor
from tools import register_tools, prompt, llm
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler



# llm = Ollama(
#     model="mistral",
#     callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
# )


# llm("what's your name ")
agent = create_openai_functions_agent(llm, register_tools, prompt)


agent_executor = AgentExecutor(agent=agent, tools=register_tools)

while True:
    user_input = input("\nstart typing: ")
    result = agent_executor.invoke({"input": user_input})
    print(f'\nAI: {result["output"]}')








# while True:
#     query = input("start typing... ")
#     llm(query)