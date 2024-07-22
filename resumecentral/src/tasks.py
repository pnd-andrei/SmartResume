"""
File for managing repetitive tasks

run(from terminal) with "invoke <command>" 
"""

import platform

from invoke.tasks import task

# Main Automatic Functions


@task
def run(c):
    c.run("python manage.py runserver")


@task
def runfirst(c):
    flush(c)
    syncdb(c)
    run(c)


@task
def flush(c):
    if platform.system() == "Windows":
        c.run("del /Q .\\media\\*")
    else:  # Unix-like system
        c.run("rm -rf ./media/*")

    c.run("python manage.py flush --noinput")
    deletecache(c)
    migrate(c)


@task
def deletecache(c):
    system = platform.system()

    if system == "Windows":
        delete_pycache_windows(c)
    else:
        delete_pycache_unix(c)


# Auxiliary functions


@task
def migrate(c):
    c.run("python manage.py makemigrations")
    c.run("python manage.py migrate")


@task
def syncdb(c):
    c.run("python manage.py migrate --run-syncdb")


def delete_pycache_windows(c):
    c.run("del /s /q __pycache__\\*")  # Delete __pycache__ directories recursively
    c.run(
        "for /d %x in (*) do del /s /q %x\\__pycache__\\*"
    )  # Delete __pycache__ directories in subdirectories recursively


def delete_pycache_unix(c):
    c.run("rm -rf ./*/__pycache__")
    c.run("rm -rf ./*/*/__pycache__")
