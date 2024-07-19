""" Get the right service you want to use
load_dotenv()

kernel = Kernel()
service_settings = ServiceSettings()

selectedService = (
    Service.OpenAI
    if service_settings.global_llm_service is None
    else Service(service_settings.global_llm_service.lower())
)

print(f"Using service type: {selectedService}")
"""

# Remove all services so that this cell can be re-run without restarting the kernel
# kernel.remove_all_services()

""" Now configure the service chosen
if selectedService == Service.OpenAI:
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
    service = OpenAIChatCompletion(
            service_id="default",
    )
    execution_settings = OpenAIChatPromptExecutionSettings(
        service_id="default",
        ai_model_id=os.environ.get("OPENAI_CHAT_MODEL_ID"),
        max_tokens=2000,
        temperature=0.7,
    )
elif selectedService == Service.Ollama:
    from semantic_kernel.connectors.ai.ollama import OllamaChatCompletion
    service = OllamaChatCompletion(
            service_id="default",
            base_url="http://localhost:11434",
    )
    execution_settings = OllamaPromptExecutionSettings(
        service_id="default",
        ai_model_id="llama3",
    )


# Add that service to the kernel
# kernel.add_service(service=service)

prompt = 
You are a helpful assistant. Your task is to find the most relevant CVs based on the given user request.

User Request: {{$user_input}}
Extracted Keywords: 


prompt_template_config = PromptTemplateConfig(
    name="extract_keywords",
    template=prompt,
    template_format="semantic-kernel",
    input_variables=[
        InputVariable(name="user_input", description="The user input", isRequired=True),
    ],
    execution_settings=execution_settings,
)


"""
