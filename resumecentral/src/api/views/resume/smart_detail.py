from django.shortcuts import get_object_or_404, render
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from api.models.resume import Resume
from api.modules.template_paths import template_paths
from api.serializers.resume import ResumeSerializer
from datetime import date


class IndividualSmartResumeApiView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        """
        Retrieve and display the resume for the given id.
        """
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
                }
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

        return render(request, template_paths.get("resume_smart_form"), resume_data)

    def post(self, request, *args, **kwargs):
        data = request.POST

        resume_data = {
            'employee_name': data.get('employee_name'),
            'job_profile': data.get('job_profile'),
            'seniority_level': {
                'rank': data.get('seniority_level[rank]'),
                'percentage': int(data.get('seniority_level[percentage]'))
            },
            'job_profile_description': data.get('job_profile_description'),
            'employee_description': data.get('employee_description'),
            'job_profile_required_skills': data.getlist('job_profile_required_skills[]'),
            
            'employee_skills': [],
            
            'employee_work_experiences': [],
            
            'employee_educations': [],
            
            'employee_certifications': []
        }


        # parse employee skills
        employee_skills = data.getlist(f'employee_skills[][skill]')
        employee_level_ranks = data.getlist(f'employee_skills[][seniority_level][rank]')
        employee_level_percentages = data.getlist(f'employee_skills[][seniority_level][percentage]')

        for i in range(len(employee_skills)):
            resume_data["employee_skills"].append({
                'seniority_level': { 
                    'rank': employee_level_ranks[i],
                    'percentage': int(employee_level_percentages[i])
                },
                'skill': employee_skills[i]
            })

        # parse employee work experiences
        work_positions = data.getlist(f'employee_work_experiences[][position]')
        work_employers = data.getlist(f'employee_work_experiences[][employer]')
        work_start_dates = data.getlist(f'employee_work_experiences[][start_date]')
        work_end_dates = data.getlist(f'employee_work_experiences[][end_date]')
        work_descriptions = data.getlist(f'employee_work_experiences[][description]')

        for i in range(len(work_positions)):
            resume_data["employee_work_experiences"].append({
                'position': work_positions[i],
                'employer': work_employers[i],
                'start_date': work_start_dates[i],
                'end_date': work_end_dates[i],
                'description': work_descriptions[i]
            })

        # parse employee education
        education_degrees = data.getlist(f'employee_educations[][degree]')
        education_institutions = data.getlist(f'employee_educations[][institution]')
        education_start_dates = data.getlist(f'employee_educations[][start_date]')
        education_end_dates = data.getlist(f'employee_educations[][end_date]')
        education_descriptions = data.getlist(f'employee_educations[][description]')

        for i in range(len(education_degrees)):
            resume_data["employee_educations"].append({
                'degree': education_degrees[i],
                'institution': education_institutions[i],
                'start_date': education_start_dates[i],
                'end_date': education_end_dates[i],
                'description': education_descriptions[i]
            })

        # parse employee certifications
        certifications = data.getlist(f'employee_certifications[][certification]')
        certification_institutions = data.getlist(f'employee_certifications[][institution]')
        certification_attainment_dates = data.getlist(f'employee_certifications[][attainment_date]')
        certification_descriptions = data.getlist(f'employee_certifications[][description]')

        for i in range(len(certifications)):
            resume_data["employee_certifications"].append({
                'certification': certifications[i],
                'institution': certification_institutions[i],
                'attainment_date': certification_attainment_dates[i],
                'description': certification_descriptions[i]
            })

        return render(request, template_paths.get("resume_smart"), resume_data)
