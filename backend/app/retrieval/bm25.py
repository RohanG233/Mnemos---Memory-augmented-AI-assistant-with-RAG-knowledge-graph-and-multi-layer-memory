import logging

import bm25s
import Stemmer

from app.core.config import BM25_TOP_K

logger = logging.getLogger(__name__)


class BM25Retriever:

    def __init__(self, documents: list[str]):
        """
        Build a BM25 index from a list of document strings.

        Parameters
        ----------
        documents : list[str]
            The corpus to index.  Each entry is one chunk.
        """

        self.documents = documents

        self.stemmer = Stemmer.Stemmer("english")

        corpus_tokens = bm25s.tokenize(
            documents,
            stopwords="en",
            stemmer=self.stemmer,
        )

        self.bm25 = bm25s.BM25()
        self.bm25.index(corpus_tokens)


    def search(
        self,
        query: str,
        k: int = BM25_TOP_K,
    ) -> tuple[list[int], list[float]]:
        """
        Return BM25 ranked results.

        Returns
        -------
        tuple[list[int], list[float]]
            (ranked_document_indices, scores)
            Indices are integer positions into self.documents.
        """

        if not self.documents:
            return [], []

        query_tokens = bm25s.tokenize(query, stemmer=self.stemmer)

        actual_k = min(k, len(self.documents))

        results, scores = self.bm25.retrieve(query_tokens, k=actual_k)

        # bm25s returns a 2-D array; first row is for our single query
        document_indices: list[int] = [int(i) for i in results[0].tolist()]

        return document_indices, scores[0].tolist()
