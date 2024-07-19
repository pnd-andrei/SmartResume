import os
from abc import ABC, abstractmethod
from pathlib import Path

import requests


class ResumeController(ABC):
    def __init__(self, url) -> None:
        self._url = url

    @abstractmethod
    def get_resumes(self, route=None):
        pass

    @abstractmethod
    def get_pdfs(self, route=None):
        pass


class LocalResumeController(ResumeController):
    def __init__(self, url) -> None:
        super().__init__(url)
        self.__route = "/resumes/?json"

    def get_resumes(self, route=None):
        if route == None:
            route = self.__route

        full_route = self._url + route

        try:
            response = requests.get(full_route)
            response.raise_for_status()  # Check if the request was successful
            return response.json()  # Return the JSON content as a list of dicts
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")

        return None

    def get_pdfs(self, route=None):
        resumes_list = self.get_resumes(route)

        if resumes_list == None:
            return None

        pdfs_paths = list(
            map(lambda resume: resume["file_upload"], resumes_list["data"])
        )

        for index in range(len(pdfs_paths)):
            pdfs_paths[index] = (
                str(Path(__file__).parent.parent) + "/media/" + pdfs_paths[index]
            )

        return pdfs_paths


class RemoteResumeController(ResumeController):
    def __init__(self, url) -> None:
        super().__init__(url)

    def get_resumes(self, route):
        pass

    def get_pdfs(self, route):
        pass
