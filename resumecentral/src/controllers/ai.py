from resumecentral.src.controllers.chroma_db import ChromaDatabaseController
import os
from dotenv import load_dotenv
from langchain_core.documents import Document
import asyncio  # noqa: F401
from resumecentral.src.sem_kernel import kernel
from semantic_kernel.contents import ChatHistory
from semantic_kernel.functions import KernelArguments
import tempfile

import requests

class AIController:
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
    async def sort_retrieved_docs_by_experience(retrieved_docs: list[Document]) -> list[Document]:
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
    


    @staticmethod
    def remove_first_and_last_line(s):
        # Split the string into lines
        lines = s.splitlines()

        # Check if there are more than two lines
        if len(lines) <= 2:
            raise ValueError("String must have more than two lines to remove the first and last lines.")

        # Remove the first and last lines
        lines_to_keep = lines[1:-1]

        # Join the remaining lines back into a string
        return '\n'.join(lines_to_keep)
    









    @staticmethod
    async def enhance_cv(retrieved_docs: list[Document], id: int, given_query: str):
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

        # Find the document from the list of PDFs with the specified id
        cv_to_enhance = requests.get(retrieved_docs[0]).text

        if cv_to_enhance is None:
            raise ValueError(f"No document found with id: {id}")
        

        prompt = """
        CV enhancing assistant can look into documents, provide and enhance information of what's inside.
        It creates a class and return an object.

        Chat history: {{$history}}
        Query: {{$query_input}}
        PDF document: {{$cv_input}}
        """

        # Define a prompt template comfig with the PDF document as input and chat history
        prompt_template_config = kernel.PromptTemplateConfig(
            name="return smart resume object",
            template=prompt,
            template_format="semantic-kernel",
            input_variables=[
                kernel.InputVariable(
                    name="cv_input", 
                    description="The CV to crate a object from", 
                    isRequired=True,
                ),
                kernel.InputVariable(
                    name="query_input",
                    description="The query to be inspired by",
                    is_required=True,
                ),
                kernel.InputVariable(
                    name="history",
                    description="The conversation history",
                    is_required=True,
                ),
            ],
            execution_settings=execution_settings,
        )

        enhancing_function = kernel_instance.add_function(
            function_name="enhanceFunc",
            plugin_name="enhancePlugin",
            prompt_template_config=prompt_template_config,
        )

        chat_history = ChatHistory()
        chat_history.add_system_message(
            """
            You are a helpful assistant. Your task is to look inside the metadata of the PDF document given as input (which is a CV) and 
        create an object having the following format: 

        resume_data = {
            'employee_name': 'John Doe',
            'job_profile': 'Software Engineer',
            'seniority_level': {
                'rank': 'Senior',
                'percentage': 85
            },
            'job_profile_description': 'An experienced software engineer with expertise in web development and data science.',
            'employee_description': 'John is a dedicated professional with over 10 years of experience in the tech industry.',
            'job_profile_required_skills': [
                'Python',
                'Django',
                'JavaScript',
                'React',
                'React2'
            ],
            'employee_skills': [
                {'skill': 'Python', 'seniority_level': {'rank': 'Expert', 'percentage': 90}},
                {'skill': 'Django', 'seniority_level': {'rank': 'Advanced', 'percentage': 80}},
                {'skill': 'JavaScript', 'seniority_level': {'rank': 'Intermediate', 'percentage': 70}},
                {'skill': 'React', 'seniority_level': {'rank': 'Intermediate', 'percentage': 70}},
                {'skill': 'React2', 'seniority_level': {'rank': 'Intermediate', 'percentage': 70}}
            ],
            'employee_work_experiences': [
                {
                    'position': 'Lead Developer',
                    'employer': 'Tech Company',
                    'start_date': date(2018, 1, 1),
                    'end_date': date(2020, 12, 31),
                    'description': 'Led a team of developers in building scalable web applications.'
                },
                {
                    'position': 'Senior Developer',
                    'employer': 'Another Tech Company',
                    'start_date': date(2015, 1, 1),
                    'end_date': date(2017, 12, 31),
                    'description': 'Worked on several high-profile projects, improving performance and usability.'
                },
            ],
            'employee_educations': [
                {
                    'degree': 'Bachelor of Science in Computer Science',
                    'institution': 'University of Example',
                    'start_date': date(2010, 9, 1),
                    'end_date': date(2014, 6, 30),
                    'description': 'Graduated with honors, specializing in software engineering.'
                }
            ],
            'employee_certifications': [
                {
                    'certification': 'Certified Django Developer',
                    'institution': 'Django Software Foundation',
                    'attainment_date': date(2019, 5, 1),
                    'description': 'Certified expertise in Django framework.'
                }
            ]
        }

            The data inside is just an example, it will be different for every object you create. Notice that for some fields like 
        employee_skills or employee_certifications there can be multiple dictionaries inside. For the employee_description field, you 
        should also shape and adjust the context based on the given query. If you do not have enough information for some fileds like 
        start dates or 
            You have to retrieve the information from the page_content of the PDF document given as input and create an object with the data 
        inside. Return only the object. Also with the necesary imports.
        """
        )
    
        arguments = KernelArguments(cv_input=cv_to_enhance, query_input=given_query, history=chat_history)

        object_created = await kernel_instance.invoke(
            function=enhancing_function, arguments=arguments
        )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w") as temp_file:
            temp_file_name = temp_file.name

            temp_file.write(AIController.remove_first_and_last_line(str(object_created)))

            return temp_file_name

        return ""
    












    @staticmethod
    def main():
        query = "stem innovation olympiad silver award"
        print(f"\nQuerying for: {query}\n")

        retrieved_docs = AIController.similarity_search(query=query)

        '''
        docs_by_experience = asyncio.run(     
            AIController.sort_retrieved_docs_by_experience(
                retrieved_docs=retrieved_docs
            )
        )
        print([doc.metadata["id"] for doc in docs_by_experience])
        '''

        object_created = asyncio.run(AIController.enhance_cv(retrieved_docs=retrieved_docs, id=3, given_query=query))
        print(f"Object created: {object_created}")


if __name__ == "__main__":
    AIController.main()
