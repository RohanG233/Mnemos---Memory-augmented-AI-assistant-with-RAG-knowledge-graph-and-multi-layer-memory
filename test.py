import inspect
from sentence_transformers import SentenceTransformer

#print(dir(SentenceTransformer))
print(inspect.getmembers(SentenceTransformer.encode))