text = open("../spider.txt", "r").read()

from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
chunks = splitter.split_text(text)

print("Recursive Chunks:", len(chunks))

print("Len : ", len(chunks[0]), "\n", chunks[0])
# for i in range(len(chunks)):
#     print(chunks[i])