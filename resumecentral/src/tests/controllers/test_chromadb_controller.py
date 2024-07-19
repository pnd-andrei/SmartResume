import unittest

from langchain_core.documents import Document

from resumecentral.src.chroma.chroma_database import ChromaDatabase
from resumecentral.src.controllers.chromadb_controller import ChromaDatabaseController


class TestChromaDatabaseController(unittest.TestCase):

    def setUp(self):
        # Initialize ChromaDatabaseController instance
        self.controller = ChromaDatabaseController()

    def test_create_database(self):
        # Test creating a new database
        db = self.controller.create_database(
            name="TestDB",
            collection=None,
            collection_name="TestCollection",
            db_path="fake/path",
            embedding_model_name="sentence-transformers/all-mpnet-base-v2",
            embedding_model_kwargs={"device": "cpu"},
            embedding_encode_kwargs={"normalize_embeddings": True},
            chunk_size=500,
            chunk_overlap=50,
            documents=[Document(page_content="Test content")],
        )
        self.assertIn("TestDB", self.controller.databases)
        self.assertIsInstance(db, ChromaDatabase)

    def test_create_database_existing_name(self):
        # Test creating a database with an existing name raises ValueError
        self.controller.create_database(
            name="TestDB", documents=[Document(page_content="Test content")]
        )
        with self.assertRaises(ValueError):
            self.controller.create_database(
                name="TestDB", documents=[Document(page_content="Test content")]
            )

    def test_get_database(self):
        # Test retrieving an existing database
        self.controller.create_database(
            name="ExistingDB", documents=[Document(page_content="Test content")]
        )
        db = self.controller.get_database("ExistingDB")
        self.assertIsNotNone(db)
        self.assertIsInstance(db, ChromaDatabase)

    def test_get_nonexistent_database(self):
        # Test retrieving a non-existent database returns None
        db = self.controller.get_database("NonExistingDB")
        self.assertIsNone(db)

    def test_delete_database(self):
        # Test deleting an existing database
        self.controller.create_database(
            name="ToDeleteDB", documents=[Document(page_content="Test content")]
        )
        self.controller.delete_database("ToDeleteDB")
        self.assertNotIn("ToDeleteDB", self.controller.databases)

    def test_delete_nonexistent_database(self):
        # Test deleting a non-existent database
        self.controller.delete_database("NonExistingDB")
        # No exception should be raised, and database count should remain the same
        self.assertEqual(len(self.controller.databases), 0)


if __name__ == "__main__":
    unittest.main()
