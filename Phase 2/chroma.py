import chromadb
chroma_client = chromadb.Client()

collection1 = chroma_client.create_collection(name="collec1")
collection2 = chroma_client.create_collection(name="collec2")

collection1.add(
    ids=["id1", "id2"],
    documents=[
        "This is a document about pineapple",
        "This is a document about oranges"
    ]
)
print(collection1.count())

results = collection1.query(
    query_texts=["This is a query document about hawaii"], # Chroma will embed this for you
    n_results=2 # how many results to return
)
print(results)