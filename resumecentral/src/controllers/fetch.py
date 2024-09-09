import os
import sys

import django

controller_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(controller_dir)

sys.path.append(src_dir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from api.models.resume import Resume  # noqa: E402
from api.serializers.resume import ResumeSerializer  # noqa: E402
from django.core.files import File  # noqa: E402
import glob  # noqa: E402
import string  # noqa: E402
import secrets  # noqa: E402


def fetch_resumes(url):
    resumes = Resume.objects.all()
    serializer = ResumeSerializer(resumes, many=True)

    return [
        [x.get("id"), url + "/static" + x.get("file_upload")] for x in serializer.data
    ]


def extract_name_from_path(path):
    # Find the position of the last '/'
    last_slash_index = path.rfind("/")

    # Extract the substring between the last '/' and '.pdf'
    start_index = last_slash_index + 1

    return path[start_index:]


def get_pdfs():
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the pattern to match PDF files in the directory
    pdf_pattern = os.path.join(script_dir, "CVs", "*.pdf")

    # Use glob to get all PDF files matching the pattern
    pdf_files = glob.glob(pdf_pattern)

    return pdf_files


def add_resume(file_path):
    # Ensure the file exists at the given path
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file at {file_path} does not exist.")

    # Open the file and create a File object for Django
    with open(file_path, "rb") as f:
        characters = string.ascii_letters + string.digits

        random_filename = (
            "".join(secrets.choice(characters) for _ in range(32)) + ".pdf"
        )
        django_file = File(f, name=random_filename)

        # Create and save the Resume object
        resume = Resume(
            description=f"{extract_name_from_path(file_path)}", file_upload=django_file
        )
        resume.save()

    print(f"Resume {file_path} has been added to the database.")


def add_all_resumes():
    for pdf_path in get_pdfs():
        add_resume(pdf_path)


def delete_all_resumes():
    # Delete all Resume objects from the database
    Resume.objects.all().delete()
    print("All resumes have been deleted from the database.")


if __name__ == "__main__":
    delete_all_resumes()
    add_all_resumes()
    pass
