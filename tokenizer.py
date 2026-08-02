import tiktoken

encoded = tiktoken.encoding_for_model("gpt-4.1")

text = "Hello, how are you?"

encoding = encoded.encode_batch(text)
print(encoding)


# # print(type(encoded))
# print(dir(encoded))


# import inspect

# print(inspect.signature(encoded.encode))