"""
File for managing repetitive tasks

run(from terminal) with "invoke <command>" 
"""

import platform

from invoke.tasks import task


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
    c.run("python manage.py migrate --run-syncdb")


@task
def delete_pycache(c):
    system = platform.system()

    if system == "Windows":
        delete_pycache_windows(c)
    else:
        delete_pycache_unix(c)


def delete_pycache_windows(c):
    c.run("del /s /q __pycache__\\*")  # Delete __pycache__ directories recursively
    c.run(
        "for /d %x in (*) do del /s /q %x\\__pycache__\\*"
    )  # Delete __pycache__ directories in subdirectories recursively


def delete_pycache_unix(c):
    c.run("rm -rf ./*/__pycache__")
    c.run("rm -rf ./*/*/__pycache__")
