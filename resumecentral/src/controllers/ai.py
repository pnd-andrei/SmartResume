from resumecentral.src.controllers.chroma_db import ChromaDatabaseController
import os
from dotenv import load_dotenv
from langchain_core.documents import Document
import asyncio  # noqa: F401
from resumecentral.src.sem_kernel import kernel
from semantic_kernel.contents import ChatHistory
from semantic_kernel.functions import KernelArguments
from resumecentral.src.chroma.database import ChromaDatabase
from resumecentral.src.controllers.smart_resume_data import SmartResumeData
import pymupdf
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
    async def enhance_cv(retrieved_docs, id: int, given_query: str):
        # Get the variables from the .env file
        dotenv_path = os.path.join(
            os.path.dirname(__file__), "..", "sem_kernel", ".env"
        )
        load_dotenv(dotenv_path=dotenv_path)

        print(retrieved_docs)

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
        cv_to_enhance = ChromaDatabase.load_resumes([[0,retrieved_docs[0]]])
        print(cv_to_enhance)

        if cv_to_enhance is None:
            raise ValueError(f"No document found with id: {id}")
        

        prompt = """
        CV enhancing assistant can look into documents, provide and enhance information of what's inside.

        Chat history: {{$history}}
        PDF document: {{$cv_input}}
        """

        # Employee name
        prompt_template_config = kernel.PromptTemplateConfig(
            name="return employee name",
            template=prompt,
            template_format="semantic-kernel",
            input_variables=[
                kernel.InputVariable(name="cv_input", description="The CV to look into", isRequired=True),
                kernel.InputVariable(name="history", description="The conversation history", is_required=True),
            ],
            execution_settings=execution_settings,
        )

        employee_name_function = kernel_instance.add_function(
            function_name="employeeNameFunc",
            plugin_name="employeeNamePlugin",
            prompt_template_config=prompt_template_config,
        )

        chat_history = ChatHistory()
        chat_history.add_system_message(
        """
            You are a helpful assistant. Your task is to look inside the given string as input (which is a CV) 
        and provide me the empolyee name (string).
        """
        )
    
        arguments = KernelArguments(cv_input=cv_to_enhance, history=chat_history)
        employee_name = await kernel_instance.invoke(function=employee_name_function, arguments=arguments)


        # Job profile
        prompt_template_config = kernel.PromptTemplateConfig(
            name="return job profile",
            template=prompt,
            template_format="semantic-kernel",
            input_variables=[
                kernel.InputVariable(name="cv_input", description="The CV to look into", isRequired=True),
                kernel.InputVariable(name="history", description="The conversation history", is_required=True),
            ],
            execution_settings=execution_settings,
        )

        job_profile_function = kernel_instance.add_function(
            function_name="jobProfileFunc",
            plugin_name="jobProfilePlugin",
            prompt_template_config=prompt_template_config,
        )

        chat_history = ChatHistory()
        chat_history.add_system_message(
        """
            You are a helpful assistant. Your task is to look inside the given string as input (which is a CV) 
        and provide me the job profile (string).
        """
        )
    
        arguments = KernelArguments(cv_input=cv_to_enhance, history=chat_history)
        job_profile = await kernel_instance.invoke(function=job_profile_function, arguments=arguments)


        # Seniority level
        prompt_template_config = kernel.PromptTemplateConfig(
            name="return seniority level and rank",
            template=prompt,
            template_format="semantic-kernel",
            input_variables=[
                kernel.InputVariable(name="cv_input", description="The CV to look into", isRequired=True),
                kernel.InputVariable(name="history", description="The conversation history", is_required=True),
            ],
            execution_settings=execution_settings,
        )

        seniority_level_function = kernel_instance.add_function(
            function_name="seniorityLevelFunc",
            plugin_name="seniorityLevelPlugin",
            prompt_template_config=prompt_template_config,
        )

        chat_history = ChatHistory()
        chat_history.add_system_message(
        """
            You are a helpful assistant. Your task is to look inside the given string as input (which is a CV) 
        and provide me the seniority level (string) which can be Intern, Junior, Mid, Senior or Principal and the rank which is a 
        percentage from 0 to 100 (int). If the seniority level is not provided, you can aproximate by the candidate experience. 
        If the rank is not provided do not return it.
        """
        )
    
        arguments = KernelArguments(cv_input=cv_to_enhance, history=chat_history)
        seniority_level = await kernel_instance.invoke(function=seniority_level_function, arguments=arguments)


        # Job profile description
        prompt_template_config = kernel.PromptTemplateConfig(
            name="return job profile description",
            template=prompt,
            template_format="semantic-kernel",
            input_variables=[
                kernel.InputVariable(name="cv_input", description="The CV to look into", isRequired=True),
                kernel.InputVariable(name="history", description="The conversation history", is_required=True),
            ],
            execution_settings=execution_settings,
        )

        job_profile_description_function = kernel_instance.add_function(
            function_name="jobProfileDescriptionFunc",
            plugin_name="jobProfileDescriptionPlugin",
            prompt_template_config=prompt_template_config,
        )

        chat_history = ChatHistory()
        chat_history.add_system_message(
        """
            You are a helpful assistant. Your task is to look inside the given string as input (which is a CV) 
        and provide me the job profile description (string) which is a short description of what the candidate does. Keep it simple.
        """
        )
    
        arguments = KernelArguments(cv_input=cv_to_enhance, history=chat_history)
        job_profile_description = await kernel_instance.invoke(function=job_profile_description_function, arguments=arguments)


        # Employee description
        query_prompt = """
        CV enhancing assistant can look into documents, provide and enhance information of what's inside.

        Chat history: {{$history}}
        document: {{$cv_input}}
        Query: {{$query_input}}
        """

        prompt_template_config = kernel.PromptTemplateConfig(
            name="return employee description",
            template=query_prompt,
            template_format="semantic-kernel",
            input_variables=[
                kernel.InputVariable(name="cv_input", description="The CV to look into", isRequired=True),
                kernel.InputVariable(name="query_input", description="The given query", is_required=True),
                kernel.InputVariable(name="history", description="The conversation history", is_required=True),
            ],
            execution_settings=execution_settings,
        )

        employee_description_function = kernel_instance.add_function(
            function_name="employeeDescriptionFunc",
            plugin_name="employeeDescriptionPlugin",
            prompt_template_config=prompt_template_config,
        )

        chat_history = ChatHistory()
        chat_history.add_system_message(
        """
            You are a helpful assistant. Your task is to look inside the given string as input (which is a CV) 
        and provide me the employee description (string) which is a short description of what the candidate does. You have to adapt 
        that description to be suitable for the given query, so that them both mold together. Keep it simple.
        """
        )
    
        arguments = KernelArguments(cv_input=cv_to_enhance, query_input=given_query, history=chat_history)
        employee_description = await kernel_instance.invoke(function=employee_description_function, arguments=arguments)


        # Employee skills
        prompt_template_config = kernel.PromptTemplateConfig(
            name="return employee skills",
            template=prompt,
            template_format="semantic-kernel",
            input_variables=[
                kernel.InputVariable(name="cv_input", description="The CV to look into", isRequired=True),
                kernel.InputVariable(name="history", description="The conversation history", is_required=True),
            ],
            execution_settings=execution_settings,
        )

        employee_skills_function = kernel_instance.add_function(
            function_name="employeeSkillsFunc",
            plugin_name="employeeSkillsPlugin",
            prompt_template_config=prompt_template_config,
        )

        chat_history = ChatHistory()
        chat_history.add_system_message(
        """
            You are a helpful assistant. Your task is to look inside the given string as input (which is a CV) 
        and provide me the employee skills which is a list of dictinaries, each dictionary being a skill under this format:
        {
            seniority_level': { 
                'rank': Can be Intern, Junior, Mid, Senior or Principal.
                'percentage': Can be from 0 to 100.
            },
            'skill':
        }
        """
        )
    
        arguments = KernelArguments(cv_input=cv_to_enhance, history=chat_history)
        employee_skills = await kernel_instance.invoke(function=employee_skills_function, arguments=arguments)


        # Employee work experiences
        prompt_template_config = kernel.PromptTemplateConfig(
            name="return employee work experience",
            template=prompt,
            template_format="semantic-kernel",
            input_variables=[
                kernel.InputVariable(name="cv_input", description="The CV to look into", isRequired=True),
                kernel.InputVariable(name="history", description="The conversation history", is_required=True),
            ],
            execution_settings=execution_settings,
        )

        employee_work_experience_function = kernel_instance.add_function(
            function_name="employeeWorkExperienceFunc",
            plugin_name="employeeWorkExperiencePlugin",
            prompt_template_config=prompt_template_config,
        )

        chat_history = ChatHistory()
        chat_history.add_system_message(
        """
            You are a helpful assistant. Your task is to look inside the given string as input (which is a CV) 
        and provide me the employee work experience which is a list of dictinaries, each dictionary being a work experience under this format:
        {
            'position':
            'employer':
            'start_date': If not provided, you can aproximate or let empty.
            'end_date': If not provided, you can aproximate or let empty.
            'description': If not provided, you can generate a short description.
        }
        """
        )
    
        arguments = KernelArguments(cv_input=cv_to_enhance, history=chat_history)
        employee_work_experience = await kernel_instance.invoke(function=employee_work_experience_function, arguments=arguments)


        # Employee educations
        prompt_template_config = kernel.PromptTemplateConfig(
            name="return employee education",
            template=prompt,
            template_format="semantic-kernel",
            input_variables=[
                kernel.InputVariable(name="cv_input", description="The CV to look into", isRequired=True),
                kernel.InputVariable(name="history", description="The conversation history", is_required=True),
            ],
            execution_settings=execution_settings,
        )

        employee_education_function = kernel_instance.add_function(
            function_name="employeeEducationFunc",
            plugin_name="employeeEducationPlugin",
            prompt_template_config=prompt_template_config,
        )

        chat_history = ChatHistory()
        chat_history.add_system_message(
        """
            You are a helpful assistant. Your task is to look inside the given string as input (which is a CV) 
        and provide me the employee education which is a list of dictinaries, each dictionary being an education under this format:
        {
            'degree':
            'institution':
            'start_date': If not provided, you can aproximate or let empty.
            'end_date': If not provided, you can aproximate or let empty.
            'description': If not provided, you can generate a short description.
        }
        """
        )
    
        arguments = KernelArguments(cv_input=cv_to_enhance, history=chat_history)
        employee_education = await kernel_instance.invoke(function=employee_education_function, arguments=arguments)


        # Employee certifications
        prompt_template_config = kernel.PromptTemplateConfig(
            name="return employee certification",
            template=prompt,
            template_format="semantic-kernel",
            input_variables=[
                kernel.InputVariable(name="cv_input", description="The CV to look into", isRequired=True),
                kernel.InputVariable(name="history", description="The conversation history", is_required=True),
            ],
            execution_settings=execution_settings,
        )

        employee_certification_function = kernel_instance.add_function(
            function_name="employeeCertificationFunc",
            plugin_name="employeeCertificationPlugin",
            prompt_template_config=prompt_template_config,
        )

        chat_history = ChatHistory()
        chat_history.add_system_message(
        """
            You are a helpful assistant. Your task is to look inside the given string as input (which is a CV) 
        and provide me the employee education which is a list of dictinaries, each dictionary being a certification under this format:
        {
            'certification':
            'institution':
            'attainment_date': If not provided, you can aproximate or let empty.
            'description': If not provided, you can generate a short description.
        }
        """
        )
    
        arguments = KernelArguments(cv_input=cv_to_enhance, history=chat_history)
        employee_certification = await kernel_instance.invoke(function=employee_certification_function, arguments=arguments)

        resume_data = SmartResumeData(
            employee_name=employee_name,
            job_profile=job_profile,
            seniority_level=seniority_level,
            job_profile_description=job_profile_description,
            employee_description=employee_description,
            job_profile_required_skills=[],
            employee_skills=employee_skills,
            employee_work_experiences=employee_work_experience,
            employee_educations=employee_education,
            employee_certifications=employee_certification
        )

        resume_data_dict = resume_data.to_dict()

        return resume_data_dict





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
    #AIController.main()
    pass
