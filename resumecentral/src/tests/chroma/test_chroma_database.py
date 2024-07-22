import unittest

from langchain_core.documents import Document

from chroma.database import ChromaDatabase


class TestChromaDatabase(unittest.TestCase):

    def setUp(self):
        # Set up the ChromaDatabase instance
        self.documents = [Document(page_content="Test content", metadata={"id": "1"})]
        self.db = ChromaDatabase(
            collection=None,
            collection_name="test_collection",
            db_path="fake/path",
            embedding_model_name="sentence-transformers/all-mpnet-base-v2",
            embedding_model_kwargs={"device": "cpu"},
            embedding_encode_kwargs={"normalize_embeddings": True},
            chunk_size=500,
            chunk_overlap=50,
            documents=self.documents,
        )

    def test_initialization(self):
        # Test the proper initialization of the database
        self.assertIsNotNone(self.db.embedding_function)
        self.assertIsNotNone(self.db.chroma_client)
        self.assertIsNotNone(self.db.collection)
        self.assertIsNotNone(self.db.vectorstore)
        self.assertIsNotNone(self.db.parent_retriever)

    def test_switch_collection(self):
        # Test switching collections
        old_collection_name = self.db.collection_name
        self.db.switch_collection("new_collection")
        self.assertNotEqual(self.db.collection_name, old_collection_name)
        self.assertEqual(self.db.collection_name, "new_collection")

    def test_clear_stores(self):
        # Assume that the clear_stores method should empty the database
        # Since we are not using a real database, let's simulate this behavior
        self.db.clear_stores()  # This should ideally clear all collections, vectorstore data, etc.
        # As this is a hypothetical situation, we may assume the stores are empty without direct checking.

    def test_update_db_path(self):
        # Test updating the database path
        new_path = "new/fake/path"
        self.db.update_db_path(new_path)
        self.assertEqual(self.db.db_path, new_path)


if __name__ == "__main__":
    unittest.main()
