from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama

llm = ChatOllama(model="hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:latest")

prompt = ChatPromptTemplate.from_messages([
    MessagesPlaceholder(variable_name="messages")
])

chain = prompt | llm

# Manual history management
chat_history = [
    HumanMessage(content="Hi, I'm Alice."),
    AIMessage(content="Hello Alice! How can I help you?"),
]

# The new query is appended to the history for the invocation
response = chain.invoke({
    "messages": chat_history + [HumanMessage(content="What's my name?")]
})

print(response.content) # The model correctly answers "Your name is Alice."