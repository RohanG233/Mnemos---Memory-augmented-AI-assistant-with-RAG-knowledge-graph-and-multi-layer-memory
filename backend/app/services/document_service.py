import logging
import os
import uuid

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)
from app.core.database import document_collection
from app.retrieval.bm25 import BM25Retriever
from app.graph.extraction import TripleExtractor
from app.graph.store import (
    add_triple,
    save_graph,
    load_graph,
    remove_document_from_graph,
)

logger = logging.getLogger(__name__)


class DocumentService:

    def __init__(self, llm_service):
        self.triple_extractor = TripleExtractor(llm_service)

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )

        # Per-user chunk lists and BM25 indexes (in-process)
        self.user_chunks: dict[str, list[str]] = {}
        self.user_bm25: dict[str, BM25Retriever] = {}


    # -------------------------
    # Ingest text
    # -------------------------

    def ingest_text(
        self,
        text: str,
        source: str = "unknown",
        user_id: str | None = None,
    ) -> dict:
        """
        Chunk, embed, store, BM25-index, and graph-extract a document.
        """

        if not text or not text.strip():
            raise ValueError("Document text is empty.")

        chunks = self.splitter.split_text(text)

        if not chunks:
            raise ValueError("Document produced no chunks after splitting.")

        document_id = str(uuid.uuid4())

        # -------------------------
        # Store in ChromaDB
        # -------------------------

        chunk_ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "user_id": user_id,
                "document_id": document_id,
                "source": source,
                "chunk": i,
            }
            for i in range(len(chunks))
        ]

        document_collection.add(
            ids=chunk_ids,
            documents=chunks,
            metadatas=metadatas,
        )

        logger.info(
            "Stored %d chunks for document_id=%s user=%s source=%s",
            len(chunks),
            document_id,
            user_id,
            source,
        )

        # -------------------------
        # Update BM25 index
        # -------------------------

        self.user_chunks.setdefault(user_id, [])
        self.user_chunks[user_id].extend(chunks)
        self.user_bm25[user_id] = BM25Retriever(self.user_chunks[user_id])

        # -------------------------
        # Knowledge Graph extraction
        # -------------------------

        graph = load_graph(user_id)

        for chunk in chunks:
            try:
                triples = self.triple_extractor.extract_triples_from_text(chunk)
                for triple in triples:
                    subject = triple.get("subject")
                    relation = triple.get("relation")
                    obj = triple.get("object")
                    if subject and relation and obj:
                        add_triple(graph, subject, relation, obj, document_id=document_id)
            except Exception:
                logger.exception(
                    "Graph extraction failed for a chunk in document_id=%s",
                    document_id,
                )

        save_graph(graph, user_id)

        return {
            "document_id": document_id,
            "chunks": len(chunks),
            "source": source,
        }


    # -------------------------
    # Delete document
    # -------------------------

    def delete_document(self, document_id: str, user_id: str) -> bool:
        """
        Delete a document and all associated chunks, BM25 data,
        and knowledge graph relationships.
        """

        results = document_collection.get(
            where={
                "$and": [
                    {"user_id": user_id},
                    {"document_id": document_id},
                ]
            },
            include=["documents"],
        )

        chunk_ids = results["ids"]
        chunks = results["documents"]

        if not chunk_ids:
            return False

        # Remove from Chroma
        document_collection.delete(ids=chunk_ids)

        # Update in-process BM25
        if user_id in self.user_chunks:
            for chunk in chunks:
                try:
                    self.user_chunks[user_id].remove(chunk)
                except ValueError:
                    pass

        if user_id in self.user_chunks and self.user_chunks[user_id]:
            self.user_bm25[user_id] = BM25Retriever(self.user_chunks[user_id])
        else:
            self.user_chunks[user_id] = []
            self.user_bm25.pop(user_id, None)

        # Update graph
        graph = load_graph(user_id)
        remove_document_from_graph(graph, document_id)
        save_graph(graph, user_id)

        logger.info(
            "Deleted document_id=%s for user=%s (%d chunks removed)",
            document_id,
            user_id,
            len(chunk_ids),
        )

        return True


    # -------------------------
    # Initialize from Chroma
    # -------------------------

    def initialize(self) -> None:
        """
        Rebuild in-process BM25 indexes for all users
        from existing ChromaDB documents.
        Called once at startup.
        """

        result = document_collection.get(
            include=["documents", "metadatas"],
        )

        if not result["ids"]:
            logger.info("No existing documents in ChromaDB — BM25 is empty.")
            return

        self.user_chunks = {}
        self.user_bm25 = {}

        for document, metadata in zip(result["documents"], result["metadatas"]):
            user_id = metadata.get("user_id")
            if not user_id:
                continue
            self.user_chunks.setdefault(user_id, [])
            self.user_chunks[user_id].append(document)

        for user_id, chunks in self.user_chunks.items():
            self.user_bm25[user_id] = BM25Retriever(chunks)

        total_docs = sum(len(c) for c in self.user_chunks.values())
        logger.info(
            "BM25 rebuilt: %d users, %d total chunks.",
            len(self.user_chunks),
            total_docs,
        )


    def get_bm25(self, user_id: str) -> BM25Retriever | None:
        return self.user_bm25.get(user_id)
