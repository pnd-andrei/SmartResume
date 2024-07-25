from dotenv import load_dotenv
from langchain_core.documents import Document

from controllers.chroma_db import ChromaDatabaseController
from resumecentral.src.sem_kernel import kernel

import asyncio

def get_retrieved_docs():
    chromadb_controller = ChromaDatabaseController()
    chromadb_name = "default_chromadb"
    chromadb_controller.create_database(name=chromadb_name)
    chromadb = chromadb_controller.get_database(name=chromadb_name)

    resumes = chromadb.get_resumes_from_sqlite3_database()
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

    # Example query
    query = "stem innovation olympiad silver award"
    print(f"\nQuerying for: {query}\n")

    # Print the similar documents from the vectorstore
    docs_from_vectorstore = chromadb.vectorstore.similarity_search(
        query=query,
        k=500,
    )
    print(f"Result from vectorstore: {docs_from_vectorstore[0].page_content}\n")

    retrieved_docs = chromadb.parent_retriever.invoke(input=query)
    print(f"\nHow many retrieved docs: {len(retrieved_docs)}\n")

    print("Results from retriever:")

    for doc in retrieved_docs:
        if isinstance(doc, Document) and doc.metadata:
            print(f"\nDocument metadata: {doc.metadata}\n")
        else:
            print("\nRetrieved document with empty content.")
    
    return retrieved_docs

async def prelucrate_retrieved_docs(retrieved_docs):
    # Get the right service you want to use
    load_dotenv()

    kernel.setup_logging()
    kernel_instance = kernel.initialize_kernel()
    selected_service = kernel.select_ai_service()
    print(f"Using service type: {selected_service}")

    # Remove all services so that this cell can be re-run without restarting the kernel
    kernel_instance.remove_all_services()

    # Now configure the selected service
    service, execution_settings = kernel.configure_service(
        selectedService=selected_service
    )

    # Add that service to the kernel
    kernel_instance.add_service(service=service)

    prompt = """
    {{$input}}
    You are a helpful assistant. Your task is to look inside the metadata of the given PDF documents as input which are CVs and to print
    the ids sorted in descending order based on working experience of each candidate (the more years of experience a candidate has, the better). 
    If any candidates does not provide any work experience years, just put them at the end. Education years should not be taken into account. 
    Consider all the documents, if there are X as input, the output should be X sorted ids.
    """

    prompt_template_config = kernel.PromptTemplateConfig(
        name="sort documents",
        template=prompt,
        template_format="semantic-kernel",
        input_variables=[
            kernel.InputVariable(
                name="input", description="The PDF documents", isRequired=True
            ),
        ],
        execution_settings=execution_settings,
    )

    sorting_function = kernel_instance.add_function(
        function_name="sortFunc",
        plugin_name="sortPlugin",
        prompt_template_config=prompt_template_config,
    )

    result = await kernel_instance.invoke(function=sorting_function, input=retrieved_docs)
    print(result)


if __name__ == "__main__":
    retrieved_docs = get_retrieved_docs()
    asyncio.run(prelucrate_retrieved_docs(retrieved_docs=retrieved_docs))
