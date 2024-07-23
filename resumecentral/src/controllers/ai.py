
from resumecentral.src.controllers.chromadb import ChromaDatabaseController


class AIController:
    def __init__(self) -> None:
        pass

    @staticmethod
    def similarity_search(query: str, sample_size: int):
        chromadb_controller = ChromaDatabaseController()
        chromadb_name = "similarity_chromadb"
        chromadb_controller.create_database(
            name=chromadb_name, chunk_size=250, chunk_overlap=100
        )
        chromadb = chromadb_controller.get_database(name=chromadb_name)

        # Aici incepe requestul de la interfata
        resumes = chromadb.get_resumes_from_sqlite3_database()

        pdf_documents = chromadb.load_resumes(resumes=resumes)

        for document in pdf_documents:
            content = document.page_content
            cleaned_content = chromadb.clean_text(text=content)
            document.page_content = cleaned_content

        # Clear the database before adding documents
        chromadb.clear_stores()

        # This will populate both the vectorstore and the docstore
        chromadb.parent_retriever.add_documents(documents=pdf_documents)

        retrieved_docs = chromadb.parent_retriever.invoke(input=query)

        for doc in retrieved_docs:
            doc_score = str(doc.metadata.get("score"))

            doc.metadata["score"] = doc_score
            print(doc_score)

        return [doc for doc in retrieved_docs]
