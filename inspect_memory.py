import chromadb
from datetime import datetime

# Connect to existing ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Get collections
memory_collection = chroma_client.get_or_create_collection(
    name="memory"
)

episode_collection = chroma_client.get_or_create_collection(
    name="episodes"
)

procedure_collection = chroma_client.get_or_create_collection(
    name="procedures"
)


def format_time(timestamp):
    if timestamp is None:
        return "N/A"

    return datetime.fromtimestamp(timestamp).strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def print_collection(name, collection):

    print("\n" + "=" * 70)
    print(f"{name.upper()} MEMORY")
    print("=" * 70)

    print(f"Total memories: {collection.count()}")

    if collection.count() == 0:
        print("No memories stored.")
        return

    results = collection.get(
        include=["documents", "metadatas"]
    )

    ids = results["ids"]
    documents = results["documents"]
    metadatas = results["metadatas"]

    for i, (memory_id, document, metadata) in enumerate(
        zip(ids, documents, metadatas),
        start=1
    ):

        print(f"\n--- Memory {i} ---")

        print(f"ID: {memory_id}")

        print(f"Content:")
        print(document)

        print("\nMetadata:")

        for key, value in metadata.items():

            if key in ["created_at", "last_accessed"]:
                value = format_time(value)

            print(f"  {key}: {value}")


# Print all memory types

print_collection(
    "Semantic",
    memory_collection
)

print_collection(
    "Episodic",
    episode_collection
)

print_collection(
    "Procedural",
    procedure_collection
)