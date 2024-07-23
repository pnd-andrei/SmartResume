import logging
import logging.config

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.hugging_face import (
    HuggingFacePromptExecutionSettings,
    HuggingFaceTextCompletion,
)
from semantic_kernel.connectors.ai.ollama import (
    OllamaChatCompletion,
    OllamaPromptExecutionSettings,
)
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
    selectedService = (
        Service.OpenAI
        if service_settings.global_llm_service is None
        else Service(service_settings.global_llm_service.lower())
    )
    return selectedService


def configure_service(selectedService):
    if selectedService == Service.OpenAI:
        service = OpenAIChatCompletion(
            ai_model_id="gpt-3.5-turbo",
            service_id="gpt-3.5-turbo",
        )
        execution_settings = OpenAIChatPromptExecutionSettings(
            service_id="gpt-3.5-turbo",
            ai_model_id="gpt-3.5-turbo",
            max_tokens=2000,
            temperature=0.7,
        )
    elif selectedService == Service.Ollama:
        service = OllamaChatCompletion(
            service_id="llama3",
            ai_model_id="llama3",
            base_url="http://localhost:11434",
        )
        execution_settings = OllamaPromptExecutionSettings(
            service_id="llama3",
            ai_model_id="llama3",
        )
    elif selectedService == Service.HuggingFace:
        service = HuggingFaceTextCompletion(
            service_id="meta-llama/Meta-Llama-3-8B",
            ai_model_id="meta-llama/Meta-Llama-3-8B",
        )
        execution_settings = HuggingFacePromptExecutionSettings(
            service_id="meta-llama/Meta-Llama-3-8B",
        )

    return service, execution_settings
