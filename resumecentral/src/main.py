from resumecentral.src.controllers.chromadb_controller import ChromaDatabaseController
from resumecentral.src.controllers import fetch
from langchain_core.documents import Document


if __name__ == "__main__":
    chromadb_controller = ChromaDatabaseController()
    chromadb_name = "default_chromadb"
    chromadb_controller.create_database(name=chromadb_name)
    chromadb = chromadb_controller.get_database(name=chromadb_name)

    # Aici incepe requestul de la interfata

    # resumes = chromadb.get_resumes_from_sqlite3_database()
    """
    resumes = [
        "C:\\Users\\Computacenter\\Desktop\\CV.pdf",
        # "C:\\Users\\Computacenter\\Desktop\\Tudor.pdf",
        # "C:\\Users\\Computacenter\\Desktop\\Felix.pdf",
        # "C:\\Users\\Computacenter\\Desktop\\Donatella.pdf",
        # "C:\\Users\\Computacenter\\Desktop\\Valentin.pdf"
    ]
    """

    resumes = fetch.fetch_resumes()
    pdf_documents = chromadb.load_resumes(resumes=resumes)

    for document in pdf_documents:
        content = document.page_content
        cleaned_content = chromadb.clean_text(text=content)
        document.page_content = cleaned_content

    print(f"\nLength of pdf_documents: {len(pdf_documents)}\n")

    # for idx, document in enumerate(pdf_documents):
        # print(f"Document {idx + 1}: {document.page_content}\n")

    # Clear the database before adding documents
    chromadb.clear_stores()
    # This will populate both the vectorstore and the docstore
    chromadb.parent_retriever.add_documents(documents=pdf_documents)

    
    print(f"\nCollection name: {chromadb.collection.name}\n")
    # print(f"\n{chromadb.collection.get()}")
    # print(f"\n{chromadb.collection.get()['ids']}\n")
    # print(f"\n{chromadb.collection.get()['documents']}\n")

    # Example query
    query = "stem innovation olympiad silver award"
    print(f"\nQuerying for: {query}\n")

    # Print the similar documents from the vectorstore
    docs_from_vectorstore = chromadb.vectorstore.similarity_search(
        query=query,
        # k=3   Number of results to return; default to 4
    )
    print(f"Result from vectorstore: {docs_from_vectorstore[0].page_content}\n")

    retrieved_docs = chromadb.parent_retriever.invoke(input=query)
    print(f"\nHow many retrieved docs: {len(retrieved_docs)}\n")

    print(f"Results from retriever:")

    # print(f"Retrieved docs: {retrieved_docs}\n")

    for doc in retrieved_docs:
        if isinstance(doc, Document) and doc.page_content:
            print(f"\nDocument content: {doc.page_content}")
        else:
            print("\nRetrieved document with empty content.")
    
