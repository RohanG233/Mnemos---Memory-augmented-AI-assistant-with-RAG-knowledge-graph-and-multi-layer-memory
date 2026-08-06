from langchain.chains import ConversationChain
from langchain.memory import ConversationSummaryBufferMemory
from langchain_openai import ChatOpenAI

# We need an LLM to power the summarization
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Initialize the summary buffer memory
# It will start summarizing once the buffer exceeds 1000 tokens.
memory = ConversationSummaryBufferMemory(
    llm=llm,
    max_token_limit=1000,
    return_messages=True
)

# Create the conversation chain with this advanced memory
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

# Run a long conversation...
conversation.predict(input="Hi, I'm Carol, a data scientist from London.")
conversation.predict(input="I'm working on a project about LLM memory systems.")
#... many more interactions...

# After the 1000-token limit is crossed, the memory object will contain
# a summary of the early conversation and a buffer of the recent messages.
print(memory.chat_memory.messages)