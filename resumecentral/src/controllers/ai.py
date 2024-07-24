from resumecentral.src.controllers.chromadb import ChromaDatabaseController
from langchain_core.documents import Document
import shutil
import os

class AIController:
    def __init__(self) -> None:
        pass

    @staticmethod
    def similarity_search(query: str, chunk_size: int = 128):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        src = os.path.dirname(current_dir)

        
        vectorstore_path = os.path.join(src, "chroma/vectorstore/")
        cache_path = os.path.join(src, "chroma/__pycache__")
        '''
        if os.path.exists(cache_path):
            shutil.rmtree(cache_path)
            

        if os.path.exists(vectorstore_path):
            shutil.rmtree(vectorstore_path)
        '''

        chromadb_controller = ChromaDatabaseController()
        chromadb_name = "similarity_chromadb"

        overlap = int(chunk_size / 5.0)

        chromadb_controller.create_database(name=chromadb_name, db_path=vectorstore_path , chunk_size=chunk_size, chunk_overlap=overlap)
        chromadb = chromadb_controller.get_database(name=chromadb_name)

        # Aici incepe requestul de la interfata
        resumes = chromadb.get_resumes_from_sqlite3_database()
       
        pdf_documents = chromadb.load_resumes(resumes=resumes)

        for document in pdf_documents:
            content = document.page_content
            cleaned_content = chromadb.clean_text(text=content)
            document.page_content = cleaned_content

        # This will populate both the vectorstore and the docstore
        chromadb.parent_retriever.add_documents(documents=pdf_documents)
    
        retrieved_docs = chromadb.parent_retriever.invoke(input=query, k_size=1001)
        
        for doc in retrieved_docs:
           doc_score = str(doc.metadata.get("score"))

           doc.metadata["score"] = doc_score

        return([doc for doc in retrieved_docs])


