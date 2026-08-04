import faiss
import numpy as np

d = 128
M = 32

index = faiss.IndexHNSWFlat(d, M)

efConstruction = 40
efSearch = 16

xq = np.random.random((1000, d)).astype("float32")
xb = np.random.random((1000, d)).astype("float32")

index.hnsw.efConstruction = efConstruction
index.add(xb)  # build the index
index.hnsw.efSearch = efSearch
# and now we can search
print(index.search(xq[:1000], k=1))