import os

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)

from app.core.config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP
)

from app.core.database import (
    document_collection
)

from app.retrieval.bm25 import (
    BM25Retriever
)

from app.graph.extraction import (
    TripleExtractor
)

from app.graph.store import (
    add_triple,
    save_graph
)


class DocumentService:

    def __init__(
        self,
        graph,
        llm_service
    ):

        self.graph = graph

        self.triple_extractor = (
            TripleExtractor(
                llm_service
            )
        )

        self.splitter = (
            RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP
            )
        )

        self.chunks = []

        self.bm25 = None


    def load_document(
        self,
        file_path
    ):
        """
        Read a text document from disk.
        """

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            text = file.read()

        return self.ingest_text(
            text,
            source=os.path.basename(
                file_path
            )
        )


    def ingest_text(
        self,
        text,
        source="unknown"
    ):
        """
        Chunk, store, index, and graph-extract
        a document.
        """

        self.chunks = (
            self.splitter.split_text(
                text
            )
        )

        # -------------------------
        # Store documents in Chroma
        # -------------------------

        if document_collection.count() == 0:

            document_collection.add(
                ids=[
                    f"chunk_{i}"
                    for i in range(
                        len(self.chunks)
                    )
                ],

                documents=self.chunks,

                metadatas=[
                    {
                        "source": source,
                        "chunk": i
                    }

                    for i in range(
                        len(self.chunks)
                    )
                ]
            )

        # -------------------------
        # Build BM25
        # -------------------------

        self.bm25 = BM25Retriever(
            self.chunks
        )

        # -------------------------
        # Knowledge Graph
        # -------------------------

        if len(self.graph.nodes) == 0:

            for chunk in self.chunks:

                triples = (
                    self.triple_extractor
                    .extract_triples_from_text(
                        chunk
                    )
                )

                for triple in triples:

                    subject = triple.get(
                        "subject"
                    )

                    relation = triple.get(
                        "relation"
                    )

                    obj = triple.get(
                        "object"
                    )

                    if (
                        subject
                        and relation
                        and obj
                    ):

                        add_triple(
                            self.graph,
                            subject,
                            relation,
                            obj
                        )

            save_graph(
                self.graph
            )

        return {
            "chunks": len(
                self.chunks
            ),
            "source": source
        }


    def initialize(self):
        """
        Rebuild BM25 index from existing
        Chroma documents.
        """

        if document_collection.count() == 0:
            return

        result = document_collection.get(
            include=["documents"]
        )

        self.chunks = result[
            "documents"
        ]

        self.bm25 = BM25Retriever(
            self.chunks
        )


    def get_chunks(self):
        return self.chunks


    def get_bm25(self):
        return self.bm25