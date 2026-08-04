import faiss
import inspect

print(dir(faiss))



# for name, obj in inspect.getmembers(retriever):
#     if inspect.isfunction(obj):
#         print(name)

#print(inspect.signature())

# for name, obj in inspect.getmembers(bm25s, inspect.isfunction):
#     print(f"{name}{inspect.signature(obj)}")

