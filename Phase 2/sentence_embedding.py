from transformers import AutoTokenizer, AutoModel
import torch

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

with torch.no_grad():
    outputs = model(**inputs)

token_embeddings = outputs.last_hidden_state
attention_mask = inputs["attention_mask"]

mask = attention_mask.unsqueeze(-1)
mask = mask.expand(token_embeddings.size()).float()
masked_embeddings = token_embeddings * mask
sum_embeddings = torch.sum(masked_embeddings, dim=1)
sum_mask = torch.clamp(mask.sum(dim=1), min=1e-9)
sentence_embedding = sum_embeddings / sum_mask
print(sentence_embedding.shape)