from dotenv import load_dotenv
from resumecentral.src.sem_kernel import kernel
import os
from semantic_kernel.contents import ChatHistory
from semantic_kernel.functions import KernelArguments
from resumecentral.src.controllers.smart_resume_data import SmartResumeData
from langchain_core.documents import Document
import asyncio  # noqa: F401
from resumecentral.src.chroma.database import ChromaDatabase  # noqa: F401
import json


class AIEnhance:
    @staticmethod
    def delete_first_and_last_line(input_string):
        # Split the input string into a list of lines
        lines = input_string.splitlines()

        # Check if the string has more than two lines
        if len(lines) > 2:
            # Remove the first and last lines
            lines = lines[1:-1]
        else:
            # If there are not enough lines, return an empty string
            return ""

        # Join the remaining lines back into a single string
        result_string = "\n".join(lines)
        return result_string

    @staticmethod
    async def get_employee_name(
        prompt, execution_settings, kernel_instance, cv_to_enhance
    ):
        # Employee name
        prompt_template_config = kernel.PromptTemplateConfig(
            name="return employee name",
            template=prompt,
            template_format="semantic-kernel",
            input_variables=[
                kernel.InputVariable(
                    name="cv_input", description="The CV to look into", isRequired=True
                ),
                kernel.InputVariable(
                    name="history",
                    description="The conversation history",
                    is_required=True,
                ),
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
            You are a helpful assistant. Your task is to look inside the given PDF document as input (which is a CV) 
        and provide me the empolyee name (string). Only the name, nothing more. Do not provide a introduction of what you return. 
        Refactor name if needed (if for example it is written only in uppercase letters, correct it).
        """
        )

        arguments = KernelArguments(cv_input=cv_to_enhance, history=chat_history)
        employee_name = await kernel_instance.invoke(
            function=employee_name_function, arguments=arguments
        )

        return employee_name

    @staticmethod
    async def get_job_profile(
        prompt, execution_settings, kernel_instance, cv_to_enhance
    ):
        # Job profile
        prompt_template_config = kernel.PromptTemplateConfig(
            name="return job profile",
            template=prompt,
            template_format="semantic-kernel",
            input_variables=[
                kernel.InputVariable(
                    name="cv_input", description="The CV to look into", isRequired=True
                ),
                kernel.InputVariable(
                    name="history",
                    description="The conversation history",
                    is_required=True,
                ),
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
            You are a helpful assistant. Your task is to look inside the given PDF document as input (which is a CV) 
        and provide me the job profile (string). Only the job profile, nothing more. Do not provide a introduction of what you return. 
        """
        )

        arguments = KernelArguments(cv_input=cv_to_enhance, history=chat_history)
        job_profile = await kernel_instance.invoke(
            function=job_profile_function, arguments=arguments
        )

        return job_profile

    @staticmethod
    async def get_seniority_level(
        prompt, execution_settings, kernel_instance, cv_to_enhance
    ):
        # Seniority level
        prompt_template_config = kernel.PromptTemplateConfig(
            name="return seniority level and rank",
            template=prompt,
            template_format="semantic-kernel",
            input_variables=[
                kernel.InputVariable(
                    name="cv_input", description="The CV to look into", isRequired=True
                ),
                kernel.InputVariable(
                    name="history",
                    description="The conversation history",
                    is_required=True,
                ),
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
            You are a helpful assistant. Your task is to look inside the given PDF document as input (which is a CV) 
        and provide me the rank (string) which can be Intern, Junior, Mid, Senior or Principal and the percentage which is a 
        number from 0 to 100 (int). If the rank is not provided, you can aproximate by the candidate experience. 
        If the percentage is not provided you can aproximate by the candidate experience. Do not provide a introduction of what you return. 
        Give me a JSON.
        """
        )

        arguments = KernelArguments(cv_input=cv_to_enhance, history=chat_history)
        seniority_level = await kernel_instance.invoke(
            function=seniority_level_function, arguments=arguments
        )

        seniority_level_json_string = str(seniority_level)

        try:
            seniority_level_json = AIEnhance.delete_first_and_last_line(
                seniority_level_json_string
            )
            seniority_level_python = json.loads(seniority_level_json)
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON: {e}")

        # print(f"Seniority level python: {seniority_level_python}")
        return seniority_level_python

    @staticmethod
    async def get_job_profile_description(
        prompt, execution_settings, kernel_instance, cv_to_enhance
    ):
        # Job profile description
        prompt_template_config = kernel.PromptTemplateConfig(
            name="return job profile description",
            template=prompt,
            template_format="semantic-kernel",
            input_variables=[
                kernel.InputVariable(
                    name="cv_input", description="The CV to look into", isRequired=True
                ),
                kernel.InputVariable(
                    name="history",
                    description="The conversation history",
                    is_required=True,
                ),
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
            You are a helpful assistant. Your task is to look inside the given PDF document as input (which is a CV) 
        and provide me the job profile description (string) which is a short description of what the candidate does and nothing more. 
        First person, without pronouns. Keep it simple. Do not provide a introduction of what you return. 
        """
        )

        arguments = KernelArguments(cv_input=cv_to_enhance, history=chat_history)
        job_profile_description = await kernel_instance.invoke(
            function=job_profile_description_function, arguments=arguments
        )

        return job_profile_description

    @staticmethod
    async def get_employee_description(
        query_prompt, execution_settings, kernel_instance, cv_to_enhance, given_query
    ):
        # Employee description
        prompt_template_config = kernel.PromptTemplateConfig(
            name="return employee description",
            template=query_prompt,
            template_format="semantic-kernel",
            input_variables=[
                kernel.InputVariable(
                    name="cv_input", description="The CV to look into", isRequired=True
                ),
                kernel.InputVariable(
                    name="query_input", description="The given query", is_required=True
                ),
                kernel.InputVariable(
                    name="history",
                    description="The conversation history",
                    is_required=True,
                ),
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
            You are a helpful assistant. Your task is to look inside the given PDF document as input (which is a CV) 
        and provide me the employee description (string) which is a short description of what the candidate does and nothing more. 
        You have to adapt that description to be suitable for the given query, so that them both mold together. First person, 
        without pronouns. Keep it simple. Do not provide a introduction of what you return. Give me a string.
        """
        )

        arguments = KernelArguments(
            cv_input=cv_to_enhance, query_input=given_query, history=chat_history
        )
        employee_description = await kernel_instance.invoke(
            function=employee_description_function, arguments=arguments
        )

        return employee_description

    @staticmethod
    async def get_employee_skills(
        prompt, execution_settings, kernel_instance, cv_to_enhance
    ):
        # Employee skills
        prompt_template_config = kernel.PromptTemplateConfig(
            name="return employee skills",
            template=prompt,
            template_format="semantic-kernel",
            input_variables=[
                kernel.InputVariable(
                    name="cv_input", description="The CV to look into", isRequired=True
                ),
                kernel.InputVariable(
                    name="history",
                    description="The conversation history",
                    is_required=True,
                ),
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
        and return the employee skills which is a list of dictinaries, each dictionary being a skill under this format:
        {
            seniority_level': { 
                'rank': Can be Intern, Junior, Mid, Senior or Principal.
                'percentage': Can be from 0 to 100.
            },
            'skill':
        }
        Do not provide a introduction of what you return. Give me a JSON.
        """
        )

        arguments = KernelArguments(cv_input=cv_to_enhance, history=chat_history)
        employee_skills = await kernel_instance.invoke(
            function=employee_skills_function, arguments=arguments
        )

        employee_skills_json_string = str(employee_skills)

        try:
            employee_skills_json = AIEnhance.delete_first_and_last_line(
                employee_skills_json_string
            )
            employee_skills_python = json.loads(employee_skills_json)
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON: {e}")

        # print(f"Employee skills python: {employee_skills_python}")
        return employee_skills_python

    @staticmethod
    async def get_employee_work_experience(
        prompt, execution_settings, kernel_instance, cv_to_enhance
    ):
        # Employee work experiences
        prompt_template_config = kernel.PromptTemplateConfig(
            name="return employee work experience",
            template=prompt,
            template_format="semantic-kernel",
            input_variables=[
                kernel.InputVariable(
                    name="cv_input", description="The CV to look into", isRequired=True
                ),
                kernel.InputVariable(
                    name="history",
                    description="The conversation history",
                    is_required=True,
                ),
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
            You are a helpful assistant. Your task is to look inside the given PDF document as input (which is a CV) 
        and return the employee work experience which is a list of dictionaries, each dictionary being a work experience under this format:
        {
            'position':
            'employer':
            'start_date': If not provided, you can aproximate .
            'end_date': If not provided, you can aproximate.
            'description': If not provided, you can generate a short description.
        }
        Do not provide a introduction of what you return. Give me a JSON.
        """
        )

        arguments = KernelArguments(cv_input=cv_to_enhance, history=chat_history)
        employee_work_experience = await kernel_instance.invoke(
            function=employee_work_experience_function, arguments=arguments
        )

        employee_work_experience_json_string = str(employee_work_experience)

        try:
            employee_work_experience_json = AIEnhance.delete_first_and_last_line(
                employee_work_experience_json_string
            )
            employee_work_experience_python = json.loads(employee_work_experience_json)
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON: {e}")

        # print(f"Employee work experience python: {employee_work_experience_python}")
        return employee_work_experience_python

    @staticmethod
    async def get_employee_education(
        prompt, execution_settings, kernel_instance, cv_to_enhance
    ):
        # Employee educations
        prompt_template_config = kernel.PromptTemplateConfig(
            name="return employee education",
            template=prompt,
            template_format="semantic-kernel",
            input_variables=[
                kernel.InputVariable(
                    name="cv_input", description="The CV to look into", isRequired=True
                ),
                kernel.InputVariable(
                    name="history",
                    description="The conversation history",
                    is_required=True,
                ),
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
           You are a helpful assistant. Your task is to look inside the given PDF document (which is a CV) and return the degrees from accredited universities and high
             schools only. Present the information as a list of dictionaries, with each dictionary representing an educational qualification in the following format:
           {
            'degree':
            'institution':
            'start_date': If not provided, you can aproximate.
            'end_date': If not provided, you can aproximate.
            'description': If not provided, you can generate a short description.
        }
        Do not provide a introduction of what you return. Give me a JSON.
        """
        )

        arguments = KernelArguments(cv_input=cv_to_enhance, history=chat_history)
        employee_education = await kernel_instance.invoke(
            function=employee_education_function, arguments=arguments
        )

        employee_education_json_string = str(employee_education)

        try:
            employee_education_json = AIEnhance.delete_first_and_last_line(
                employee_education_json_string
            )
            employee_education_python = json.loads(employee_education_json)
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON: {e}")

        # print(f"Employee education python: {employee_education_python}")
        return employee_education_python

    @staticmethod
    async def get_employee_certification(
        prompt, execution_settings, kernel_instance, cv_to_enhance
    ):
        # Employee certifications
        prompt_template_config = kernel.PromptTemplateConfig(
            name="return employee certification",
            template=prompt,
            template_format="semantic-kernel",
            input_variables=[
                kernel.InputVariable(
                    name="cv_input", description="The CV to look into", isRequired=True
                ),
                kernel.InputVariable(
                    name="history",
                    description="The conversation history",
                    is_required=True,
                ),
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
            You are a helpful assistant. Your task is to look inside the given PDF document as input (which is a CV) 
        and return the employee certifications which is a list of dictinaries, each dictionary being a certification under this format:
        {
            'certification':
            'institution':
            'attainment_date': If not provided, you can aproximate.
            'description': If not provided, you can generate a short description.
        }
        Do not provide a introduction of what you return. Give me a JSON.
        """
        )

        arguments = KernelArguments(cv_input=cv_to_enhance, history=chat_history)
        employee_certification = await kernel_instance.invoke(
            function=employee_certification_function, arguments=arguments
        )

        employee_certification_json_string = str(employee_certification)

        try:
            employee_certification_json = AIEnhance.delete_first_and_last_line(
                employee_certification_json_string
            )
            employee_certification_python = json.loads(employee_certification_json)
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON: {e}")

        # print(f"Employee certification python: {employee_certification_python}")
        return employee_certification_python

    @staticmethod
    async def enhance_cv(retrieved_docs: list[Document], id: int, given_query: str):
        # Get the variables from the .env file
        dotenv_path = os.path.join(
            os.path.dirname(__file__), "..", "sem_kernel", ".env"
        )
        load_dotenv(dotenv_path=dotenv_path)

        # print(retrieved_docs)

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
        # cv_to_enhance = ChromaDatabase.load_resumes([[0,retrieved_docs[0]]])

        cv_to_enhance = next(
            (doc for doc in retrieved_docs if doc.metadata.get("id") == id), None
        )

        if cv_to_enhance is None:
            raise ValueError(f"No document found with id: {id}")

        prompt = """
        CV enhancing assistant can look into documents, provide and enhance information of what's inside.

        Chat history: {{$history}}
        PDF document: {{$cv_input}}
        """

        query_prompt = """
        CV enhancing assistant can look into documents, provide and enhance information of what's inside.

        Chat history: {{$history}}
        PDF document: {{$cv_input}}
        Query: {{$query_input}}
        """

        resume_data = SmartResumeData(
            employee_name=await AIEnhance.get_employee_name(
                prompt=prompt,
                execution_settings=execution_settings,
                kernel_instance=kernel_instance,
                cv_to_enhance=cv_to_enhance,
            ),
            job_profile=await AIEnhance.get_job_profile(
                prompt=prompt,
                execution_settings=execution_settings,
                kernel_instance=kernel_instance,
                cv_to_enhance=cv_to_enhance,
            ),
            seniority_level=await AIEnhance.get_seniority_level(
                prompt=prompt,
                execution_settings=execution_settings,
                kernel_instance=kernel_instance,
                cv_to_enhance=cv_to_enhance,
            ),
            job_profile_description=await AIEnhance.get_job_profile_description(
                prompt=prompt,
                execution_settings=execution_settings,
                kernel_instance=kernel_instance,
                cv_to_enhance=cv_to_enhance,
            ),
            employee_description=await AIEnhance.get_employee_description(
                query_prompt=query_prompt,
                execution_settings=execution_settings,
                kernel_instance=kernel_instance,
                cv_to_enhance=cv_to_enhance,
                given_query=given_query,
            ),
            job_profile_required_skills=[],
            employee_skills=await AIEnhance.get_employee_skills(
                prompt=prompt,
                execution_settings=execution_settings,
                kernel_instance=kernel_instance,
                cv_to_enhance=cv_to_enhance,
            ),
            employee_work_experiences=await AIEnhance.get_employee_work_experience(
                prompt=prompt,
                execution_settings=execution_settings,
                kernel_instance=kernel_instance,
                cv_to_enhance=cv_to_enhance,
            ),
            employee_educations=await AIEnhance.get_employee_education(
                prompt=prompt,
                execution_settings=execution_settings,
                kernel_instance=kernel_instance,
                cv_to_enhance=cv_to_enhance,
            ),
            employee_certifications=await AIEnhance.get_employee_certification(
                prompt=prompt,
                execution_settings=execution_settings,
                kernel_instance=kernel_instance,
                cv_to_enhance=cv_to_enhance,
            ),
        )

        """
        print(f"Employee name: {resume_data.employee_name}\n")
        print(f"Job profile: {resume_data.job_profile}\n")
        print(f"Seniority level: {resume_data.seniority_level}\n")
        print(f"Job profile description: {resume_data.job_profile_description}\n")
        print(f"Employee description: {resume_data.employee_description}\n")
        print(f"Employee skills: {resume_data.employee_skills}\n")
        print(f"Employee work experiences: {resume_data.employee_work_experiences}\n")
        print(f"Employee educations: {resume_data.employee_educations}\n")
        print(f"Employee certifications: {resume_data.employee_certifications}\n")
        """

        resume_data_dict = resume_data.to_dict()
        print("\n\n\n"+str(resume_data_dict))

        return resume_data_dict

    """
    @staticmethod
    def main():
        resumes = ChromaDatabase.get_resumes_from_sqlite3_database()
        retrieved_docs = ChromaDatabase.load_resumes(resumes=resumes)

        query = "Python intermediate level English"
        print(f"Querying for: {query}\n")

        result = asyncio.run(
            AIEnhance.enhance_cv(
                retrieved_docs=retrieved_docs, id=23, given_query=query
            )
        )
        print(f"Result:\n {result} \n")


if __name__ == "__main__":
    AIEnhance.main()
"""
