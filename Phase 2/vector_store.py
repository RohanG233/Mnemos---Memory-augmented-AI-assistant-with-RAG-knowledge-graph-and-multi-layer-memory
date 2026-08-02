import chromadb
chroma_client = chromadb.Client()

collection = chroma_client.create_collection(name="my_collection")

collection.add(
    ids=["id1", "id2"],
    documents=[
        "This is a document about pineapple",
        "This is a document about oranges"
    ],
    metadatas = [{'fruit' : 'pineapple'}, {'fruit' : 'oranges'}]
)

results = collection.query(
    query_texts=["This is a query document about hawaii"], # Chroma will embed this for you
    n_results=1, # how many results to return
    include = ['metadatas', 'documents', 'distances']
)
print(results)