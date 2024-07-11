'''
File for managing repetitive tasks

run(from terminal) with "invoke <command>" 
'''

from invoke import task

@task
def run(c):
    c.run("python manage.py runserver")

@task
def migrate(c):
    c.run("python manage.py makemigrations")
    c.run("python manage.py migrate")

@task
def flush(c):
    c.run("rm -rf ./media/*")
    c.run("python manage.py flush --noinput")
    migrate(c)

@task
def syncdb(c):
    c.run("python manage.py syncdb")