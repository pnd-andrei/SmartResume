from controllers.chromadb import ChromaDatabaseController

if __name__ == "__main__":
    chromadb_controller = ChromaDatabaseController()
    chromadb_name = "default_chromadb"
    chromadb_controller.create_database(name=chromadb_name)
    chromadb = chromadb_controller.get_database(name=chromadb_name)

    # Aici incepe requestul de la interfata

    # resumes = chromadb.get_resumes_from_sqlite3_database()
    resumes = ["C:\\Users\\Computacenter\\Desktop\\CV.pdf"]
    pdf_documents = chromadb.load_resumes(resumes=resumes)

    for document in pdf_documents:
        content = document.page_content
        cleaned_content = chromadb.clean_text(text=content)
        document.page_content = cleaned_content

    print(f"\nLength of pdf_documents: {len(pdf_documents)}\n")

    # Clear the database before adding documents
    chromadb.clear_stores() 
    # This will populate both the vectorstore and the docstore
    chromadb.parent_retriever.add_documents(documents=pdf_documents)

    print(f"\nCollection name: {chromadb.collection.name}\n")
    print(f"\n{chromadb.collection.get()}\n")

    # Print the similar documents from the vectorstore
    docs_from_vectorstore = chromadb.vectorstore.similarity_search(
        "Python intermediate level English"
    )
    print(docs_from_vectorstore[0].page_content)

    # Example query
    query = "Python intermediate level English"
    print(f"\nQuerying for: {query}\n")
    retrieved_docs = chromadb.parent_retriever.invoke(input=query)
    print(f"\nHow many retrieved docs: {len(retrieved_docs)}\n")

    for doc in retrieved_docs:
        if doc.page_content:
            print(f"\nDocument content: {doc.page_content}")
        else:
            print("\nRetrieved document with empty content.")
