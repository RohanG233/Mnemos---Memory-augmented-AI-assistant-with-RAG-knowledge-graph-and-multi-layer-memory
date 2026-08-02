from gensim.models import Word2Vec
import gensim
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
nltk.download('punkt')
nltk.download("punkt_tab")
import warnings

warnings.filterwarnings(action='ignore')


with open("corpus.txt", "r", encoding="utf-8") as file:
    content = file.read()

cleaned_text = content.replace("\n", " ")
print("File loaded")

data = []
for i in sent_tokenize(cleaned_text):
    temp = []
    for j in word_tokenize(i):
        temp.append(j.lower())
    data.append(temp)

model1 = gensim.models.Word2Vec(data, min_count=1, vector_size=30, window=5)
model2 = gensim.models.Word2Vec(data, min_count=1, vector_size=30, window=5, sg=1)

for i in range(len(data[0]) - 1):
    word1 = data[0][i]
    word2 = data[0][i + 1]

    similarity = model1.wv.similarity(word1, word2)

    print(f"{word1} <-> {word2} : {similarity:.4f}")