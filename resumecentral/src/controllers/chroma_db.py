from typing import Any, Optional

from langchain_core.documents import Document
from resumecentral.src.chroma.database import ChromaDatabase


class ChromaDatabaseController:
    def __init__(self) -> None:
        """
        Initializes the ChromaDatabaseController instance, setting up an empty dictionary to store database configurations.
        """
        self.databases = {}

    def create_database(
        self,
        name: str,
        db_path: str,
        chunk_size: int,
        chunk_overlap: int,
        collection: Optional[Any] = None,
        collection_name: str = "chunk_collection",
        embedding_model_name: str = "sentence-transformers/all-mpnet-base-v2",
        embedding_model_kwargs: dict = {"device": "mps"},
        embedding_encode_kwargs: dict = {"normalize_embeddings": False},
        documents: list[Document] = [],
    ):
        """
        Creates a new ChromaDatabase instance with the specified parameters and adds it to the controller's database dictionary.

        Parameters:
            name (str): The name of the database configuration.
            collection_name (str): The name of the default collection within the database.
            db_path (str): The file system path to the database.
            embedding_model_name (str): The name of the embedding model to use for document embeddings.
            embedding_model_kwargs (dict): Additional keyword arguments for the embedding model.
            embedding_encode_kwargs (dict): Additional keyword arguments for the embedding function.
            chunk_size (int): The size of each text chunk.
            chunk_overlap (int): The number of characters to overlap between chunks.
            documents (list[Document]): A list of Document objects to be added to the retriever.

        Returns:
            The newly created ChromaDatabase instance.

        Raises:
            ValueError: If the database already exists in the databases dictinary.
        """
        if name in self.databases:
            raise ValueError(f"A database with the name '{name}' already exists.")

        chroma_db = ChromaDatabase(
            db_path=db_path,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            collection=collection,
            collection_name=collection_name,
            embedding_model_name=embedding_model_name,
            embedding_model_kwargs=embedding_model_kwargs,
            embedding_encode_kwargs=embedding_encode_kwargs,
            documents=documents,
        )

        self.databases[name] = chroma_db
        return chroma_db

    def get_database(self, name: str):
        """
        Retrieves a ChromaDatabase instance by its configuration name.

        Parameters:
            name (str): The name of the database configuration to retrieve.

        Returns:
            The ChromaDatabase instance if found, otherwise None.
        """
        return self.databases.get(name)

    def delete_database(self, name: str) -> None:
        """
        Deletes a database configuration from the controller.

        Parameters:
            name (str): The name of the database configuration to delete.
        """
        if name in self.databases:
            del self.databases[name]
            print(f"Database configuration '{name}' deleted successfully.")
        else:
            print(f"Database configuration '{name}' not found.")
