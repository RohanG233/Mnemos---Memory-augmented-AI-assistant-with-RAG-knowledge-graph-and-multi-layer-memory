from transformers import AutoTokenizer, AutoModel
import torch
import inspect

#print(dir(AutoModel))
#help(AutoModel.register)
# inspect.getmembers(AutoModel)

tokenizer = AutoTokenizer.from_pretrained(
    "sentence-transformers/all-MiniLM-L6-v2"
)


model = AutoModel.from_pretrained(
    "sentence-transformers/all-MiniLM-L6-v2"
)


sentence = "I love football."

inputs = tokenizer(
    sentence,
    return_tensors="pt"
)

#print(dir(inputs))
#print(inputs.token_to_word)

with torch.no_grad():
    outputs = model(**inputs)

token_embeddings = outputs.last_hidden_state
#print(dir(outputs))
help(outputs.last_hidden_state)
# print(token_embeddings.shape)