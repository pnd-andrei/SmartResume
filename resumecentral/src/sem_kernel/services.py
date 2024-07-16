"This module defines an enumeration representing different services"

from enum import Enum


class Service(Enum):
    """
    Attributes:
    OpenAI (str): Represents the OpenAI service
    HuggingFace (str): Represents the HuggingFace service
    """

    OpenAI = "openai"
    HuggingFace = "huggingface"
    Ollama = "ollama"
