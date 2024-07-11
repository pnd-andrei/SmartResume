"""
File for managing repetitive tasks

run(from terminal) with "invoke <command>" 
"""

from invoke.tasks import task


@task
def run(c):
    c.run("python manage.py runserver")


@task
def migrate(c):
    c.run("python manage.py makemigrations")
    c.run("python manage.py migrate")
