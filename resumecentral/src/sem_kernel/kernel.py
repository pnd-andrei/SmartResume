import logging
import logging.config

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.hugging_face import (
    HuggingFacePromptExecutionSettings,
    HuggingFaceTextCompletion,
)
from semantic_kernel.connectors.ai.ollama import OllamaPromptExecutionSettings
from semantic_kernel.connectors.ai.open_ai import (
    OpenAIChatCompletion,
    OpenAIChatPromptExecutionSettings,
)
from semantic_kernel.prompt_template import (  # noqa: F401
    InputVariable,
    PromptTemplateConfig,
)

from resumecentral.src.sem_kernel.service_settings import ServiceSettings
from resumecentral.src.sem_kernel.services import Service
from openai import AsyncOpenAI


def setup_logging():
    # Setup a detailed logging format
    logging.basicConfig(
        format="[%(asctime)s - %(name)s:%(lineno)d - %(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Set the logging level for semantic_kernel.kernel to DEBUG
    logging.getLogger("kernel").setLevel(logging.DEBUG)


def initialize_kernel():
    kernel = Kernel()
    return kernel


def select_ai_service():
    service_settings = ServiceSettings.create()

    # print(f"Service settings: {service_settings}\n")
    # print(f"Service settings . global llm service: {service_settings.global_llm_service}\n")

    selectedService = (
        Service.OpenAI
        if service_settings.global_llm_service is None
        else Service(service_settings.global_llm_service.lower())
    )
    return selectedService


def configure_service(selectedService):
    if selectedService == Service.OpenAI:
        service = OpenAIChatCompletion(
            ai_model_id="gpt-4o",
            service_id="gpt-4o",
        )
        execution_settings = OpenAIChatPromptExecutionSettings(
            service_id="gpt-4o",
            ai_model_id="gpt-4o",
            temperature=0,
        )
    elif selectedService == Service.Ollama:
        openAIClient: AsyncOpenAI = AsyncOpenAI(
            api_key="fake-key", # required but ignored
            base_url="http://localhost:11434"
        )
        service = OpenAIChatCompletion(
            service_id="phi:latest", 
            ai_model_id="phi:latest",
            async_client=openAIClient
        )
        execution_settings = OllamaPromptExecutionSettings(
            service_id="phi:latest",
            ai_model_id="phi:latest",
        )
    elif selectedService == Service.HuggingFace:
        service = HuggingFaceTextCompletion(
            service_id="google/flan-t5-large",
            ai_model_id="google/flan-t5-large",
            task="text2text-generation",
        )
        execution_settings = HuggingFacePromptExecutionSettings(
            service_id="meta-llama/Meta-Llama-3-8B",
        )

    return service, execution_settings
