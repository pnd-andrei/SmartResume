import os
import re
from typing import Any, Optional

import chromadb
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# import pymupdf4llm
import resumecentral.src.controllers.resume_controller as resume_controller

# from langchain_text_splitters import MarkdownHeaderTextSplitter, MarkdownTextSplitter


class ChromaDatabase:
    def __init__(
        self,
        collection: Optional[Any],
        collection_name: str,
        db_path: str,
        embedding_model_name: str,
        embedding_model_kwargs: dict[str, Any],
        embedding_encode_kwargs: dict[str, Any],
        chunk_size: int,
        chunk_overlap: int,
        documents: list[Document],
    ) -> None:
        """
        Initializes an instance of the ChromaDatabase with the specified parameters.

        Parameters:
            collection (any, optional): The collection to use. Defaults to None. Store chunks of documents into it.
            collection_name (str): The name of the collection. Defaults to "resumes_chunks".
            db_path (str): The path to the Chroma database directory. Defaults to "chroma_vectorstore".
            embedding_model_name (str): The name of the embedding model. Defaults to "sentence-transformers/all-mpnet-base-v2".
            embedding_model_kwargs (dict): Model configuration options. Defaults to {'device': 'cpu'}.
            embedding_encode_kwargs (dict): Encoding configuration options. Defaults to {'normalize_embeddings': False}.
        """

        self.collection = collection
        self.collection_name = collection_name
        self.db_path = db_path
        self.embedding_model_name = embedding_model_name
        self.embedding_model_kwargs = embedding_model_kwargs
        self.embedding_encode_kwargs = embedding_encode_kwargs
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.documents = documents

        self._initialize_embedding_function()
        self._initialize_chroma_client()
        self._initialize_collection()
        self._initialize_vectorstore()
        self.splitter = self._initialize_splitter(
            chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
        )
        self.parent_retriever = self._initialize_parent_document_retriever(
            documents=self.documents,
            child_splitter=self.splitter,
        )

    def _initialize_embedding_function(self) -> None:
        """
        Initializes the Hugging Face embedding model.
        Chose all-mpnet-base-v2 because:
        - MPNet models often outperform BERT and RoBERTa in various benchmarks due to their advanced architecture.
        - all-mpnet-base-v2 is specifically designed for creating high-quality sentence embeddings, making it ideal for tasks
        like semantic similarity and document retrieval.

        Raises:
            ValueError: If the embedding model initialization fails.
        """
        try:
            self.embedding_function = HuggingFaceEmbeddings(
                model_name=self.embedding_model_name,
                model_kwargs=self.embedding_model_kwargs,
                encode_kwargs=self.embedding_encode_kwargs,
            )
        except Exception as e:
            raise ValueError(f"Failed to initialize embedding function: {e}")

    def _initialize_chroma_client(self) -> None:
        """
        Initializes the Chroma client with the specified database path.

        Raises:
            ValueError: If the database path is not specified or if the client initialization fails.
        """
        if not self.db_path:
            raise ValueError("Database path must be specified.")

        try:
            current_dir = os.path.dirname(__file__)
            persist_directory = os.path.join(current_dir, self.db_path)
            self.chroma_client = chromadb.PersistentClient(path=persist_directory)
        except Exception as e:
            raise ValueError(f"Failed to initialize Chroma client: {e}")

    def _initialize_collection(self) -> None:
        """
        Initializes the collection for storing documents. Creates a new collection if it doesn't exist.

        Raises:
            ValueError: If the collection initialization fails.
        """
        try:
            if self.collection is None:
                self.collection = self.chroma_client.get_or_create_collection(
                    name=self.collection_name
                )
        except Exception as e:
            raise ValueError(f"Failed to initialize collection: {e}")

    def _initialize_vectorstore(self) -> None:
        """
        Initializes the vector store for document embeddings.

        Raises:
            ValueError: If the vector store initialization fails.
        """
        try:
            self.vectorstore = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embedding_function,
                client=self.chroma_client,
            )
        except Exception as e:
            raise ValueError(f"Failed to initialize vector store: {e}")

    def _initialize_splitter(
        self, chunk_size: int, chunk_overlap: int
    ) -> RecursiveCharacterTextSplitter:
        """
        Initializes a RecursiveCharacterTextSplitter with the specified chunk size and chunk overlap.

        Parameters:
            chunk_size (int): The size of each text chunk.
            chunk_overlap (int): The number of characters to overlap between chunks.

        Returns:
            An instance of RecursiveCharacterTextSplitter configured with the given parameters.

        Raises:
            ValueError: If the splitter initialization fails.
        """
        try:
            recursive_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
            return recursive_splitter
        except Exception as e:
            raise ValueError(f"Failed to initialize splitter: {e}")

    def _initialize_parent_document_retriever(
        self, documents: list[Document], child_splitter: RecursiveCharacterTextSplitter
    ) -> ParentDocumentRetriever:
        """
        Initializes a ParentDocumentRetriever for the given documents, using the specified child splitter for text splitting.

        Parameters:
            documents (list[Document]): A list of Document objects to be added to the retriever.
            child_splitter (RecursiveCharacterTextSplitter): The text splitter to be used for splitting the documents into smaller chunks.

        Returns:
            ParentDocumentRetriever: An instance of ParentDocumentRetriever initialized with the documents and child splitter.

        Raises:
            ValueError: If the documents list is empty.
            ValueErorr: If the retriever initialization fails.
        """
        if not documents:
            raise ValueError("Document list is empty")

        try:
            self.store = InMemoryStore()
            self.retriever = ParentDocumentRetriever(
                vectorstore=self.vectorstore,
                docstore=self.store,
                child_splitter=child_splitter,
            )
            return self.retriever
        except Exception as e:
            raise ValueError(f"Failed to initialize retriever: {e}")

    def switch_collection(self, switch_to_collection: str) -> None:
        """
        Switches the current working collection to the specified collection. If the specified
        collection does not exist, it is created and then set as the current working collection.

        This method updates the instance's current collection, collection name, and vectorstore to
        reflect the newly created or switched-to collection. It relies on the underlying database
        client's `get_or_create_collection` method to handle the creation or retrieval of the collection,
        abstracting away the details of collection management.

        Parameters:
            switch_to_collection (str): The name of the collection to switch to or create.

        Note: Consider deleting the old collection before creating a new one.

        Raises:
            ValueError: If the switch fails.
        """
        try:
            self.collection_name = switch_to_collection
            self.collection = self.chroma_client.get_or_create_collection(
                name=self.collection_name
            )
            self._initialize_vectorstore()
        except Exception as e:
            raise ValueError(f"Failed to switch collection: {e}")

    def delete_collection(self, collection_name: str = "chunk_collection") -> None:
        """
        Deletes a collection from the Chroma database.

        Parameters:
            collection_name (str): The name of the collection to delete.

        Note: You might not want to do that.
            - this will lead to removing the default chunk collection and you'll have to recreate one;

        Raises:
            ValueError: If the deletion fails.
        """
        try:
            self.chroma_client.delete_collection(name=collection_name)
            print(f"Collection {collection_name} deleted successfully.")
        except Exception as e:
            print(f"Error deleting collection {collection_name}: {e}")

    def clear_stores(self) -> None:
        """
        Clears all documents from the collection and vectors from the vectorstore.
        Also clears all documents from the docstore in the ParentDocumentRetriever.

        Raises:
            ValueError: If clearing the vectorstore, collection, or docstore fails.
        """
        try:
            # Delete all documents in the collection and vectors from vectorstore by their IDs before adding.
            # We assume that they use the same IDs.
            all_documents = self.collection.get()
            document_ids = all_documents["ids"]

            if document_ids:
                self.vectorstore.delete(ids=document_ids)
                self.collection.delete(ids=document_ids)
        except Exception as e:
            raise ValueError(f"Failed to clear the vectorstore or collection: {e}")

        # Clears all documents from the docstore.
        try:
            keys = [key for key in self.parent_retriever.docstore.yield_keys()]
            if keys:
                self.parent_retriever.docstore.mdelete(keys=keys)
        except Exception as e:
            raise ValueError(f"Failed to clear retriever docstore: {e}")

    def update_db_path(self, new_db_path: str) -> None:
        """
        Updates the database path for storing documents.

        Parameters:
            new_db_path (str): The new path to the Chroma database directory.

        Note: This will NOT move the current content to the new path, but delete it instead.
        """
        self.clear_stores()
        self.db_path = new_db_path
        self._initialize_chroma_client()
        self._initialize_collection()
        self._initialize_vectorstore()
        self.parent_retriever = self._initialize_parent_document_retriever(
            documents=self.documents,
            child_splitter=self.splitter,
        )

        print(f"Database path updated to {new_db_path}")

    def update_embedding_model(
        self,
        new_embedding_model_name: str,
        new_embedding_model_kwargs: Optional[dict[str, Any]] = None,
        new_embedding_encode_kwargs: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Updates the embedding model for generating embeddings.

        Parameters:
            new_embedding_model_name (str): The new embedding model to use.
            new_embedding_model_kwargs (dict[str, Any], optional): Model configuration options.
            new_embedding_encode_kwargs (dict[str, Any], optional): Model configuration options.
        """
        self.embedding_model_name = new_embedding_model_name
        self.embedding_model_kwargs = new_embedding_model_kwargs
        self.embedding_encode_kwargs = new_embedding_encode_kwargs

        self.clear_stores()
        self._initialize_embedding_function()
        self._initialize_vectorstore()

        self.parent_retriever = self._initialize_parent_document_retriever(
            documents=self.documents,
            child_splitter=self.splitter,
        )

        print(f"Embedding model updated to {new_embedding_model_name}")

    @staticmethod
    def get_resumes_from_sqlite3_database(self) -> list | None:
        """
        Retrieves resumes from a predefined local server. This function makes a call to the server,
        attempting to fetch PDF files representing resumes.

        Returns:
            A list of resumes fetched from the server. Returns an empty list if an error occurs.

        Raises:
            ValueError: If the resumes retrieval fails.
        """
        url = "http://127.0.0.1:8000"
        local_resume_controller = resume_controller.LocalResumeController(url)
        resumes = [][:]
        try:
            resumes = local_resume_controller.get_pdfs()
            return resumes
        except Exception as e:
            raise ValueError(f"Error retrieving resumes: {e}")

    @staticmethod
    def load_resumes(resumes: list) -> list:
        """
        Loads resumes from a list of Document objects, attempting to read and parse each as a PDF file.
        Utilizes the PyMuPDFLoader for loading the content of each resume.

        Parameters:
            resumes (list[Document]): A list of Document objects representing the resumes to be loaded.

        Returns:
            A list of loaded resume documents. If an error occurs during loading of any resume, it skips that resume.

        Raises:
            ValueError: If the loading fails.
        """
        pdf_documents = []
        for resume in resumes:
            try:
                pdf_loader = PyMuPDFLoader(resume)
                pdf_documents.extend(pdf_loader.load())
            except Exception as e:
                raise ValueError(f"Error loading resume with id {resume.id}: {e}")
        return pdf_documents

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Cleans the input text by replacing newlines with spaces, reducing multiple spaces to a single space,
        and trimming leading and trailing spaces.

        Parameters:
            text (str): The text to be cleaned.

        Returns:
            The cleaned text.

        Raises:
            ValueError: If the cleaning fails.
        """
        try:
            text = text.replace(old="\n", new=" ")
            text = re.sub(
                pattern=r"\s{2,}",
                repl=" ",
                string=text,
            )
            text = text.strip()
            return text
        except Exception as e:
            raise ValueError(f"Failed to clean the text: {e}")

    """
    @staticmethod
    def choose_splitter(
        docs: list[Document], chunk_size=1000, chunk_overlap=200
    ) -> (
        MarkdownHeaderTextSplitter
        | MarkdownTextSplitter
        | RecursiveCharacterTextSplitter
    ):

        # Chooses an appropriate text splitter for chunking based on the content of the documents. It tries to split the
        # documents based on markdown headers first, then falls back to markdown text splitter or a recursive character
        # splitter based on the structure of the documents.

        # Parameters:
            # docs (list[Document]): A list of Document objects to be split.
            # chunk_size (int, optional): The size of each chunk after splitting. Defaults to 1000.
            # chunk_overlap (int, optional): The overlap size between chunks. Defaults to 200.

        # Returns:
            # An instance of a text splitter, chosen based on the content of the documents.

        if not docs:
            raise ValueError("Document list is empty")
        markdown_content = ""
        for document in docs:
            file_path = document.metadata["file_path"]
            if file_path:
                try:
                    markdown_content += pymupdf4llm.to_markdown(doc=file_path)
                except Exception as e:
                    print(f"Error converting file {file_path} to markdown: {e}")
                    continue

        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
            ("####", "Header 4"),
            ("#####", "Header 5"),
            ("######", "Header 6"),
        ]

        md_header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on
        )
        md_splitter = MarkdownTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

        # recursive_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

        # Firstly, try splitting by headers (Skills, Experience..); every CV have at least 4 headers
        if len(md_header_splitter.split_text(text=markdown_content)) > 4:
            print("Splitter used: Markdown Header Text Splitter\n")
            return md_header_splitter

        # If there are no enough headers, search also for at least 4 separators including horizontal, blank lines and more
        if len(md_splitter.create_documents(texts=[markdown_content])) > 4:
            print("Splitter used: Markdown Text Splitter\n")
            return md_splitter

        # Otherwise, use the standard RecursiveCharacterTextSplitter
        print("Splitter used: Recursive Text Splitter\n")
        return recursive_splitter
        # The commented 3-splitter approach cannot be used because the ParentDocumentRetriever can only have one child_retriever
        # The class does not support the functionality where one can give the splitted data as parameter instead of a splitter
        """
