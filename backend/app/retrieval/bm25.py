import bm25s
import Stemmer

from app.core.config import BM25_TOP_K


class BM25Retriever:

    def __init__(self, documents):
        """
        Build a BM25 index from documents.
        """

        self.documents = documents

        self.stemmer = Stemmer.Stemmer(
            "english"
        )

        corpus_tokens = bm25s.tokenize(
            documents,
            stopwords="en",
            stemmer=self.stemmer
        )

        self.bm25 = bm25s.BM25()

        self.bm25.index(
            corpus_tokens
        )


    def search(
        self,
        query,
        k=BM25_TOP_K
    ):
        """
        Return BM25 ranked document IDs
        and their scores.
        """

        query_tokens = bm25s.tokenize(
            query,
            stemmer=self.stemmer
        )

        results, scores = self.bm25.retrieve(
            query_tokens,
            k=k
        )

        document_ids = results[0].tolist()

        return document_ids, scores[0].tolist()