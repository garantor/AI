import gradio as gr
from langchain.agents import create_openai_functions_agent
from langchain.agents import AgentExecutor
from tools import register_tools, llm
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder




#templates for creating prompt
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are very powerful assistant XRPL Blockchain assistant",
        ),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

# openai function calling agent api
agent = create_openai_functions_agent(llm, register_tools, prompt)



#langchain agent executor
agent_executor = AgentExecutor(agent=agent, tools=register_tools, verbose=True)
def invokeAgent(user_input:str, *args:any):
    """
    main function for invoking the openAI agent
    """
    response = agent_executor.invoke({"input": user_input})
    return response["output"]


# UI related
demo = gr.Interface(
    fn=invokeAgent,
    inputs=["text", "slider"],
    outputs=["text"],
)

demo.launch(share=True)
