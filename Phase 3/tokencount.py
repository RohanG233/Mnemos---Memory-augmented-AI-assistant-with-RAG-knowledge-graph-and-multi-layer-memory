import tiktoken

# Get encoding for your model
encoding = tiktoken.encoding_for_model("gpt-4")

# Count tokens in a simple text
text = "Hello, how are you today bruh?"
token_count = len(encoding.encode(text))
print(f"Token count: {token_count}")

# For chat messages, you must account for metadata
def count_chat_tokens(messages, model="gpt-4"):
    """
    Counts the number of tokens in a list of chat messages.
    """
    encoding = tiktoken.encoding_for_model(model)
    tokens = 0
    for message in messages:
        tokens += 4  # Every message follows <|start|>{role/name}\n{content}<|end|>\n
        for key, value in message.items():
            tokens += len(encoding.encode(value))
    tokens += 2  # Every reply is primed with <|start|>assistant
    return tokens

# Example usage for chat messages
chat_messages = [{"role": "user", "content": "Hello, how are you today?"}, {"role": "assistant", "content": "I am fine, Thank you. How do u do?"}]
chat_token_count = count_chat_tokens(chat_messages)
print(f"Chat token count: {chat_token_count}")