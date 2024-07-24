from collections import defaultdict

from langchain.retrievers import MultiVectorRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun

import uuid
from typing import Any, List, Optional, Sequence, Tuple

from langchain_core.documents import Document
from langchain_text_splitters import TextSplitter

from langchain.retrievers import MultiVectorRetriever

class CustomMultiVectorRetriever(MultiVectorRetriever):
    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun, k_size:int
    ) -> List[Document]:
        """Get documents relevant to a query.
        Args:
            query: String to find relevant documents for
            run_manager: The callbacks handler to use
        Returns:
            List of relevant documents
        """
        results = self.vectorstore.similarity_search_with_relevance_scores(
            query,
            k=k_size
        )

        # Map doc_ids to list of sub-documents, adding scores to metadata
        id_to_doc = defaultdict(list)

        for chunk, score in results:
            doc_id = chunk.metadata.get("doc_id")
            if doc_id:
                chunk.metadata["score"] = score
                id_to_doc[doc_id].append(chunk)

        # Fetch documents corresponding to doc_ids, retaining sub_docs in metadata
        docs = []

        for _id, sub_docs in id_to_doc.items():
            docstore_docs = self.docstore.mget([_id])
            if docstore_docs:
                if doc := docstore_docs[0]:
                    doc.metadata["score"] = int(10000 * sub_docs[0].metadata.get("score")) / 100.0
                    doc.metadata["score"] = str(doc.metadata["score"])
                    docs.append(doc)

        return docs
    


class CustomParentDocumentRetriever(CustomMultiVectorRetriever):
    """Retrieve small chunks then retrieve their parent documents.

    When splitting documents for retrieval, there are often conflicting desires:

    1. You may want to have small documents, so that their embeddings can most
        accurately reflect their meaning. If too long, then the embeddings can
        lose meaning.
    2. You want to have long enough documents that the context of each chunk is
        retained.

    The ParentDocumentRetriever strikes that balance by splitting and storing
    small chunks of data. During retrieval, it first fetches the small chunks
    but then looks up the parent ids for those chunks and returns those larger
    documents.

    Note that "parent document" refers to the document that a small chunk
    originated from. This can either be the whole raw document OR a larger
    chunk.

    Examples:

        .. code-block:: python

            from langchain_community.embeddings import OpenAIEmbeddings
            from langchain_community.vectorstores import Chroma
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            from langchain.storage import InMemoryStore

            # This text splitter is used to create the parent documents
            parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, add_start_index=True)
            # This text splitter is used to create the child documents
            # It should create documents smaller than the parent
            child_splitter = RecursiveCharacterTextSplitter(chunk_size=400, add_start_index=True)
            # The vectorstore to use to index the child chunks
            vectorstore = Chroma(embedding_function=OpenAIEmbeddings())
            # The storage layer for the parent documents
            store = InMemoryStore()

            # Initialize the retriever
            retriever = ParentDocumentRetriever(
                vectorstore=vectorstore,
                docstore=store,
                child_splitter=child_splitter,
                parent_splitter=parent_splitter,
            )
    """  # noqa: E501

    child_splitter: TextSplitter
    """The text splitter to use to create child documents."""

    """The key to use to track the parent id. This will be stored in the
    metadata of child documents."""
    parent_splitter: Optional[TextSplitter] = None
    """The text splitter to use to create parent documents.
    If none, then the parent documents will be the raw documents passed in."""

    child_metadata_fields: Optional[Sequence[str]] = None
    """Metadata fields to leave in child documents. If None, leave all parent document 
        metadata.
    """

    def _split_docs_for_adding(
        self,
        documents: List[Document],
        ids: Optional[List[str]] = None,
        add_to_docstore: bool = True,
    ) -> Tuple[List[Document], List[Tuple[str, Document]]]:
        if self.parent_splitter is not None:
            documents = self.parent_splitter.split_documents(documents)
        if ids is None:
            doc_ids = [str(uuid.uuid4()) for _ in documents]
            if not add_to_docstore:
                raise ValueError(
                    "If ids are not passed in, `add_to_docstore` MUST be True"
                )
        else:
            if len(documents) != len(ids):
                raise ValueError(
                    "Got uneven list of documents and ids. "
                    "If `ids` is provided, should be same length as `documents`."
                )
            doc_ids = ids

        docs = []
        full_docs = []
        for i, doc in enumerate(documents):
            _id = doc_ids[i]
            sub_docs = self.child_splitter.split_documents([doc])
            if self.child_metadata_fields is not None:
                for _doc in sub_docs:
                    _doc.metadata = {
                        k: _doc.metadata[k] for k in self.child_metadata_fields
                    }
            for _doc in sub_docs:
                _doc.metadata[self.id_key] = _id
            docs.extend(sub_docs)
            full_docs.append((_id, doc))

        return docs, full_docs

    def add_documents(
        self,
        documents: List[Document],
        ids: Optional[List[str]] = None,
        add_to_docstore: bool = True,
        **kwargs: Any,
    ) -> None:
        """Adds documents to the docstore and vectorstores.

        Args:
            documents: List of documents to add
            ids: Optional list of ids for documents. If provided should be the same
                length as the list of documents. Can be provided if parent documents
                are already in the document store and you don't want to re-add
                to the docstore. If not provided, random UUIDs will be used as
                ids.
            add_to_docstore: Boolean of whether to add documents to docstore.
                This can be false if and only if `ids` are provided. You may want
                to set this to False if the documents are already in the docstore
                and you don't want to re-add them.
        """
        docs, full_docs = self._split_docs_for_adding(documents, ids, add_to_docstore)
        self.vectorstore.add_documents(docs, **kwargs)
        if add_to_docstore:
            self.docstore.mset(full_docs)
