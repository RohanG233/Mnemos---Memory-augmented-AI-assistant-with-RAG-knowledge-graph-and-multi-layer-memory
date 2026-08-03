import requests
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from langchain_text_splitters import RecursiveCharacterTextSplitter

chroma_client = chromadb.PersistentClient(path="./chroma_db")
embedding_function = SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Load Text File
with open("spider.txt", "r", encoding="utf-8") as file:
    text = file.read()


N = 6
messages = []
collection = chroma_client.get_or_create_collection(name="documents", embedding_function=embedding_function)

# Chunking
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=70)
chunks = splitter.split_text(text)

# Store it in Chroma DB
collection.add(
    ids=[f"chunk_{i}" for i in range(len(chunks))],
    documents=chunks,
    metadatas=[
        {
            "source": "spider.txt",
            "chunk": i
        }
        for i in range(len(chunks))
    ]
)

persona = {
  "role": "system",
  "content": "You are a helpful, knowledgeable, and reliable AI assistant. Maintain context across the conversation and answer the user's most recent message while considering relevant previous messages. Be accurate, concise, and clear. If you are uncertain, state your uncertainty instead of inventing information. Ask clarifying questions only when necessary. Format responses for readability using paragraphs, bullet points, or code blocks when appropriate. Be polite and professional."
}

messages.append(persona)

while True:
    user_input = input("You : ").strip()
    messages.append({"role": "user", "content": user_input})

    query = "".join(msg["content"] for msg in messages if msg["role"] != "system")
    query_embedding = model.encode(query)

    url = "http://localhost:11434/api/chat"

    payload = {
        "model": "hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:latest",
        "messages": messages,
        "stream": False
    }

    if(len(messages) > 1 + N * 2):
        messages.pop(1)
        messages.pop(1)

    response = requests.post(url, json=payload)
    data = response.json()
    assistant_reply = data["message"]["content"]
    print("Assistant : ", assistant_reply)
    messages.append({"role":"assistant", "content":assistant_reply})