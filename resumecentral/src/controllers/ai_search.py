import asyncio  # noqa: F401
import os

from dotenv import load_dotenv
from langchain_core.documents import Document
from semantic_kernel.contents import ChatHistory
from semantic_kernel.functions import KernelArguments

from resumecentral.src.controllers.chroma_db import ChromaDatabaseController
from resumecentral.src.sem_kernel import kernel


class AISearch:
    def __init__(self) -> None:
        pass

    @staticmethod
    def similarity_search(query: str, chunk_size: int = 128):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        src = os.path.dirname(current_dir)

        vectorstore_path = os.path.join(src, "chroma/vectorstore/")

        """
        if os.path.exists(cache_path):
            shutil.rmtree(cache_path)
            

        if os.path.exists(vectorstore_path):
            shutil.rmtree(vectorstore_path)
        """

        chromadb_controller = ChromaDatabaseController()
        chromadb_name = "similarity_chromadb"

        overlap = int(chunk_size / 5.0)

        chromadb_controller.create_database(
            name=chromadb_name,
            db_path=vectorstore_path,
            chunk_size=chunk_size,
            chunk_overlap=overlap,
        )

        chromadb = chromadb_controller.get_database(name=chromadb_name)
        chromadb.clear_vectorstore_folder(folder_path=vectorstore_path)

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

        return [doc for doc in retrieved_docs if isinstance(doc, Document)]

    @staticmethod
    async def sort_retrieved_docs_by_experience(
        retrieved_docs: list[Document],
    ) -> list[Document]:
        # Get the variables from the .env file
        dotenv_path = os.path.join(
            os.path.dirname(__file__), "..", "sem_kernel", ".env"
        )
        load_dotenv(dotenv_path=dotenv_path)

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
        PDF documents assistant can look into documents and provide information about what's inside.

        Chat history: {{$history}}
        PDF documents: {{$user_input}}
        Chatbot:
        """

        # Define a prompt template comfig with the PDF documents as input and chat history
        prompt_template_config = kernel.PromptTemplateConfig(
            name="sort documents",
            template=prompt,
            template_format="semantic-kernel",
            input_variables=[
                kernel.InputVariable(
                    name="user_input",
                    description="The PDF documents",
                    isRequired=True,
                ),
                kernel.InputVariable(
                    name="history",
                    description="The conversation history",
                    is_required=True,
                ),
            ],
            execution_settings=execution_settings,
        )

        sorting_function = kernel_instance.add_function(
            function_name="sortFunc",
            plugin_name="sortPlugin",
            prompt_template_config=prompt_template_config,
        )

        chat_history = ChatHistory()
        chat_history.add_system_message(
            """
            You are a helpful assistant. Your task is to look inside the metadata of the PDF documents given as input (which are CVs) and print
        the ids sorted in descending order based on working experience of each candidate (the more years of experience a candidate has, the better). 
        If any candidates does not provide any work experience years, just put them at the end. Education years should not be taken into account. 
        Consider all the documents, if there are X as input, the output should be X sorted ids. To be more clear, you should return a list of ids.
        
            I will show you an example. Let's say that inside you have 3 PDF documents given as input. You see in the metadata and page_content 
        the following:
        Andrew (id 1) -> 3 years of experience
        Sebastian (id 2) -> 6 years of experience
        Mihai (id 3) -> 1 year of experience

        Then you should print: 2, 1, 3

            Consider that you will have different number of CVs, there won't be 3 all the times. You have to look at all, if you get 
        an input of 10 PDF documents, then you should return a list of 10 ids.

            You will print only one line representing the ids, no other words.
        """
        )

        arguments = KernelArguments(user_input=retrieved_docs, history=chat_history)
        response = await kernel_instance.invoke(
            function=sorting_function, arguments=arguments
        )
        # chat_history.add_assistant_message(str(response))

        if not isinstance(response, str):
            response = str(response)

        ids_by_experience_list = list(map(int, response.split(",")))

        # Create a dictionary mapping document IDs to documents
        doc_dict = {int(doc.metadata["id"]): doc for doc in retrieved_docs}

        # Sort the documents based on ids_by_experience_list
        sorted_docs = [doc_dict[doc_id] for doc_id in ids_by_experience_list]
        return sorted_docs
