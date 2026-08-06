from langchain_core.messages import trim_messages, HumanMessage, AIMessage

# This trimmer will keep the most recent messages up to a max count of 2.
trimmer = trim_messages(
    strategy="last",
    max_tokens=2,
    token_counter=len # A simple counter where each message is 1 token
)

messages = [
    HumanMessage(content="Hi!"),
    AIMessage(content="Hello!"),
    HumanMessage(content="How are you?"),
    AIMessage(content="I'm good, thanks!")
]

trimmed = trimmer.invoke(messages)
# Result: [HumanMessage(content='How are you?'), AIMessage(content="I'm good, thanks!")]
print(trimmed)