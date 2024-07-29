from typing import List, Dict

class SmartResumeData:
    def __init__(self,
                 employee_name: str,
                 job_profile: str,
                 seniority_level: Dict[str, any],
                 job_profile_description: str,
                 employee_description: str,
                 job_profile_required_skills: List[str],
                 employee_skills: List[Dict[str, any]],
                 employee_work_experiences: List[Dict[str, any]],
                 employee_educations: List[Dict[str, any]],
                 employee_certifications: List[Dict[str, any]]):
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

    def __repr__(self):
        return (f"ResumeData(employee_name={self.employee_name!r}, "
                f"job_profile={self.job_profile!r}, "
                f"seniority_level={self.seniority_level!r}, "
                f"job_profile_description={self.job_profile_description!r}, "
                f"employee_description={self.employee_description!r}, "
                f"job_profile_required_skills={self.job_profile_required_skills!r}, "
                f"employee_skills={self.employee_skills!r}, "
                f"employee_work_experiences={self.employee_work_experiences!r}, "
                f"employee_educations={self.employee_educations!r}, "
                f"employee_certifications={self.employee_certifications!r})")

    def to_dict(self) -> Dict[str, any]:
        return {
            'employee_name': self.employee_name,
            'job_profile': self.job_profile,
            'seniority_level': self.seniority_level,
            'job_profile_description': self.job_profile_description,
            'employee_description': self.employee_description,
            'job_profile_required_skills': self.job_profile_required_skills,
            'employee_skills': self.employee_skills,
            'employee_work_experiences': self.employee_work_experiences,
            'employee_educations': self.employee_educations,
            'employee_certifications': self.employee_certifications
        }

    @classmethod
    def from_dict(cls, data: Dict[str, any]):
        return cls(
            employee_name=data.get('employee_name', ''),
            job_profile=data.get('job_profile', ''),
            seniority_level=data.get('seniority_level', {}),
            job_profile_description=data.get('job_profile_description', ''),
            employee_description=data.get('employee_description', ''),
            job_profile_required_skills=data.get('job_profile_required_skills', []),
            employee_skills=data.get('employee_skills', []),
            employee_work_experiences=data.get('employee_work_experiences', []),
            employee_educations=data.get('employee_educations', []),
            employee_certifications=data.get('employee_certifications', [])
        )

