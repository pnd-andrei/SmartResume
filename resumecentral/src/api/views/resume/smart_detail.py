from django.shortcuts import render
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from api.modules.template_paths import template_paths

from resumecentral.src.chroma.database import ChromaDatabase
from resumecentral.src.controllers.ai_enhance import AIEnhance
import asyncio
import importlib.util
import os


def import_object_from_file(file_path, object_name):
    # Check if the file exists
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file at {file_path} does not exist.")

    # Check if the file is readable
    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"Cannot read the file at {file_path}.")

    # Load the module from the file path
    spec = importlib.util.spec_from_file_location("temp_module", file_path)

    if spec is None:
        raise RuntimeError(
            f"Failed to create a module spec from the file at {file_path}."
        )

    temp_module = importlib.util.module_from_spec(spec)

    try:
        spec.loader.exec_module(temp_module)
        return getattr(temp_module, object_name)
    except AttributeError:
        raise AttributeError(
            f"The object '{object_name}' could not be found in {file_path}."
        )
    except Exception as e:
        raise RuntimeError(f"An error occurred while importing the object: {e}")


class IndividualSmartResumeApiView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        """
        Retrieve and display the smart resume for the given id.
        """
        resumes = ChromaDatabase.get_resumes_from_sqlite3_database()
        query = request.GET.get("description")
        id = request.GET.get("id")

        model = request.GET.get("model")

        res = []

        for resume in resumes:
            if str(resume[0]) == str(id):
                res.append(resume)

        retrieved_docs = ChromaDatabase.load_resumes(resumes=res)

        dictx = asyncio.run(
            AIEnhance.enhance_cv(
                retrieved_docs=retrieved_docs,
                id=int(id),
                given_query=query,
                model=model,
            )
        )

        return render(request, template_paths.get("resume_smart_form"), dictx)

    def post(self, request, *args, **kwargs):
        data = request.POST

        resume_data = {
            "employee_name": data.get("employee_name"),
            "job_profile": data.get("job_profile"),
            "seniority_level": {
                "rank": data.get("seniority_level[rank]"),
                "percentage": int(data.get("seniority_level[percentage]")),
            },
            "job_profile_description": data.get("job_profile_description"),
            "employee_description": data.get("employee_description"),
            "job_profile_required_skills": data.getlist(
                "job_profile_required_skills[]"
            ),
            "employee_skills": [],
            "employee_work_experiences": [],
            "employee_educations": [],
            "employee_certifications": [],
        }

        # parse employee skills
        employee_skills = data.getlist("employee_skills[][skill]")
        employee_level_ranks = data.getlist("employee_skills[][seniority_level][rank]")
        employee_level_percentages = data.getlist(
            "employee_skills[][seniority_level][percentage]"
        )

        for i in range(len(employee_skills)):
            resume_data["employee_skills"].append(
                {
                    "seniority_level": {
                        "rank": employee_level_ranks[i],
                        "percentage": int(employee_level_percentages[i]),
                    },
                    "skill": employee_skills[i],
                }
            )

        # parse employee work experiences
        work_positions = data.getlist("employee_work_experiences[][position]")
        work_employers = data.getlist("employee_work_experiences[][employer]")
        work_start_dates = data.getlist("employee_work_experiences[][start_date]")
        work_end_dates = data.getlist("employee_work_experiences[][end_date]")
        work_descriptions = data.getlist("employee_work_experiences[][description]")

        for i in range(len(work_positions)):
            resume_data["employee_work_experiences"].append(
                {
                    "position": work_positions[i],
                    "employer": work_employers[i],
                    "start_date": work_start_dates[i],
                    "end_date": work_end_dates[i],
                    "description": work_descriptions[i],
                }
            )

        # parse employee education
        education_degrees = data.getlist("employee_educations[][degree]")
        education_institutions = data.getlist("employee_educations[][institution]")
        education_start_dates = data.getlist("employee_educations[][start_date]")
        education_end_dates = data.getlist("employee_educations[][end_date]")
        education_descriptions = data.getlist("employee_educations[][description]")

        for i in range(len(education_degrees)):
            resume_data["employee_educations"].append(
                {
                    "degree": education_degrees[i],
                    "institution": education_institutions[i],
                    "start_date": education_start_dates[i],
                    "end_date": education_end_dates[i],
                    "description": education_descriptions[i],
                }
            )

        # parse employee certifications
        certifications = data.getlist("employee_certifications[][certification]")
        certification_institutions = data.getlist(
            "employee_certifications[][institution]"
        )
        certification_attainment_dates = data.getlist(
            "employee_certifications[][attainment_date]"
        )
        certification_descriptions = data.getlist(
            "employee_certifications[][description]"
        )

        for i in range(len(certifications)):
            resume_data["employee_certifications"].append(
                {
                    "certification": certifications[i],
                    "institution": certification_institutions[i],
                    "attainment_date": certification_attainment_dates[i],
                    "description": certification_descriptions[i],
                }
            )

        return render(request, template_paths.get("resume_smart"), resume_data)
