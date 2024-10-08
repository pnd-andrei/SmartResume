import os
import re
from typing import Any, Optional
import shutil
import pymupdf4llm  # noqa: F401

import chromadb
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter, MarkdownTextSplitter  # noqa: F401

from resumecentral.src.controllers.fetch import fetch_resumes
from resumecentral.src.chroma.extended.custom_parent_retriever import (
    CustomParentDocumentRetriever,
)

# import pymupdf4llm
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
            chunk_size (int): The size of each text chunk.
            chunk_overlap (int): The number of characters to overlap between chunks.
            documents (list[Document]): A list of Document objects to be added to the retriever.
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
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
            return recursive_splitter
        except Exception as e:
            raise ValueError(f"Failed to initialize splitter: {e}")

    def _initialize_parent_document_retriever(
        self, child_splitter: RecursiveCharacterTextSplitter
    ) -> ParentDocumentRetriever:
        """
        Initializes a ParentDocumentRetriever, using the specified child splitter for text splitting.

        Parameters:
            child_splitter (RecursiveCharacterTextSplitter): The text splitter to be used for splitting the documents into smaller chunks.

        Returns:
            ParentDocumentRetriever: An instance of ParentDocumentRetriever initialized with the documents and child splitter.

        Raises:
            ValueErorr: If the retriever initialization fails.
        """
        try:
            self.store = InMemoryStore()

            self.retriever = CustomParentDocumentRetriever(
                vectorstore=self.vectorstore,
                docstore=self.store,
                child_splitter=child_splitter,
            )

            return self.retriever
        except Exception as e:
            raise ValueError(f"Failed to initialize retriever: {e}")

    def clear_vectorstore_folder(self, folder_path: str) -> None:
        """
        Clears the specified vectorstore folder.

        Parameters:
            folder_path (str): The path to the vectorstore folder to clear.
        """
        if os.path.exists(folder_path):
            for filename in os.listdir(path=folder_path):
                if filename == "chroma.sqlite3":
                    continue

                file_path = os.path.join(folder_path, filename)
                try:
                    if os.path.isfile(path=file_path) or os.path.islink(path=file_path):
                        os.unlink(path=file_path)
                    elif os.path.isdir(s=file_path):
                        shutil.rmtree(path=file_path)
                except Exception as e:
                    print(f"Failed to delete {file_path}. Reason: {e}")
        else:
            print(f"The folder {folder_path} does not exist.")

    @staticmethod
    def get_resumes_from_sqlite3_database() -> list | None:
        """
        Retrieves resumes from a predefined local server. This function makes a call to the server,
        attempting to fetch PDF files representing resumes.

        Returns:
            A list of resumes fetched from the server. Returns an empty list if an error occurs.

        Raises:
            ValueError: If the resumes retrieval fails.
        """
        url = "http://127.0.0.1:1080"
        resumes = [][:]
        try:
            resumes = fetch_resumes(url)
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
        if resumes:
            for resume_path in resumes:
                try:
                    pdf_loader = PyMuPDFLoader(file_path=resume_path[1])
                    loaded_pages = pdf_loader.load()

                    # Combine all pages of a resume into a single PDF Document object
                    combined_content = "\n".join(
                        page.page_content for page in loaded_pages
                    )

                    meta = {"id": resume_path[0]}

                    combined_metadata = {}

                    if loaded_pages:
                        combined_metadata = loaded_pages[0].metadata
                        combined_metadata.update(meta)

                    pdf_document = Document(
                        page_content=combined_content, metadata=combined_metadata
                    )
                    pdf_documents.append(pdf_document)

                except Exception as e:
                    raise ValueError(
                        f"Error loading resume from file {resume_path[1]}: {e}"
                    )
        else:
            raise ValueError("API database is empty")
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
            text = text.replace("\n", " ")
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

        md_header_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

        md_splitter = MarkdownTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

        recursive_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

        # Firstly, try splitting by headers (Skills, Experience..); every CV have at least 4 headers
        if len(md_header_splitter.split_text(text=markdown_content)) > 4:
            return md_header_splitter

        # If there are no enough headers, search also for at least 4 separators including horizontal, blank lines and more
        if len(md_splitter.create_documents(texts=[markdown_content])) > 4:
            return md_splitter

        # Otherwise, use the standard RecursiveCharacterTextSplitter
        return recursive_splitter
        """
