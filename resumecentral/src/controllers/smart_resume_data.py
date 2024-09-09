from typing import List, Dict


class SmartResumeData:
    def __init__(
        self,
        employee_name: str,
        job_profile: str,
        seniority_level: Dict[str, any],
        employee_description: str,
        job_profile_required_skills: List[str],
        employee_skills: List[Dict[str, any]],
        employee_work_experiences: List[Dict[str, any]],
        employee_educations: List[Dict[str, any]],
        employee_certifications: List[Dict[str, any]],
        job_profile_description: str = ""
    ):
        self.employee_name = employee_name
        self.job_profile = job_profile
        self.seniority_level = seniority_level
        self.job_profile_description = job_profile_description
        self.employee_description = employee_description
        self.job_profile_required_skills = job_profile_required_skills
        self.employee_skills = employee_skills
        self.employee_work_experiences = employee_work_experiences
        self.employee_educations = employee_educations
        self.employee_certifications = employee_certifications

    def to_dict(self) -> Dict[str, any]:
        return {
            "employee_name": self.employee_name,
            "job_profile": self.job_profile,
            "seniority_level": self.seniority_level,
            "job_profile_description": self.job_profile_description,
            "employee_description": self.employee_description,
            "job_profile_required_skills": self.job_profile_required_skills,
            "employee_skills": self.employee_skills,
            "employee_work_experiences": self.employee_work_experiences,
            "employee_educations": self.employee_educations,
            "employee_certifications": self.employee_certifications,
        }
