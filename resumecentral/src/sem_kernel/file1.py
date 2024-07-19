import asyncio
import os
import sqlite3

import chromadb
import fitz
import numpy as np
import pymupdf
import requests
import torch
from chromadb.config import Settings
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.ollama import OllamaPromptExecutionSettings
from semantic_kernel.connectors.ai.open_ai import (
    OpenAIChatPromptExecutionSettings, OpenAITextEmbedding)
from semantic_kernel.contents import ChatHistory
from semantic_kernel.functions import KernelArguments
from semantic_kernel.prompt_template import InputVariable, PromptTemplateConfig
from sentence_transformers import SentenceTransformer
from transformers import AutoModel, AutoTokenizer
from transformers.utils import ModelOutput

from ..controller.resume_controller import LocalResumeController

# from .service_settings import ServiceSettings
# from .services import Service


def extract_text_from_pdf(pdf_path):
    doc = pymupdf.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


# Extract text from specified PDF file
pdf_path = "C:\\Users\\Computacenter\\Desktop\\CV.pdf"
content = extract_text_from_pdf(pdf_path=pdf_path)


# Split text into chunks
def split_text(text, chunk_size=1000, chunk_overlap=200):
    chunks = []
    for i in range(0, len(text), chunk_size - chunk_overlap):
        chunks.append(text[i : i + chunk_size])
    return chunks


documents = split_text(content)

# Load pre-trained Hugging Face model
"""
Chosed all-mpnet-base-v2 because:
- MPNet models often outperform BERT and RoBERTa in various benchmarks due to their advanced architecture.
- all-mpnet-base-v2 is specifically designed for creating high-quality sentence embeddings, making it ideal for tasks like semantic similarity and document retrieval.
"""
model_name = "sentence-transformers/all-mpnet-base-v2"
model = SentenceTransformer(model_name_or_path=model_name)


def create_embeddings(docs):
    embeddings = model.encode(sentences=docs, convert_to_numpy=True)
    return embeddings


# Create embeddings for the document chunks
embeddings = create_embeddings(docs=documents)
print(embeddings)

current_dir = os.path.dirname(__file__)
persist_directory = os.path.join(current_dir, "chroma_database")

# Create a chrome client
chroma_settings = Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="chroma_db",
)
chroma_client = chromadb.PersistentClient(path=persist_directory)
cv_collection = chroma_client.get_or_create_collection(name="cv_keywords")

# Store embeddings in Chroma database
for idx, doc in enumerate(documents):
    cv_collection.add(
        ids=str(idx),
        embeddings=embeddings[idx].tolist(),
        metadatas={"content": doc},
    )


# Function to query the Chroma database
def query_chroma(query, n_results=2):
    query_embedding = create_embeddings([query])[0]
    results = cv_collection.query(
        query_embeddings=query_embedding.tolist(), n_results=n_results
    )
    return results


# Example query
query = "I want a .NET developer"
results = query_chroma(query=query)

# Print the matching chunks
for result in results["metadatas"]:
    print(result[0]["content"])


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
"""

# Add that service to the kernel
# kernel.add_service(service=service)

prompt = """
You are a helpful assistant. Your task is to find the most relevant CVs based on the given user request.

User Request: {{$user_input}}
Extracted Keywords: """

"""
prompt_template_config = PromptTemplateConfig(
    name="extract_keywords",
    template=prompt,
    template_format="semantic-kernel",
    input_variables=[
        InputVariable(name="user_input", description="The user input", isRequired=True),
    ],
    execution_settings=execution_settings,
)

extract_keywords_func = kernel.add_function(
    function_name="extractKeywordsFunc",
    plugin_name="keywordExtractorPlugin",
    prompt_template_config=prompt_template_config,
)

conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()

def get_cv_by_keywords(keywords):
    query = "SELECT content FROM cv WHERE keywords LIKE ?"
    cursor.execute(query, (f"%{keywords}%",))
    return cursor.fetchall()

async def extract_keywords_from_input(user_input):
    chat_history = ChatHistory()
    chat_history.add_user_message(user_input)
    arguments = KernelArguments(user_input=user_input, history=chat_history)
    response = await kernel.invoke(extract_keywords_func, arguments=arguments)
    keywords = str(response).strip()
    return keywords

async def get_relevant_cvs():
    user_input = "I want a .NET developer"
    keywords = await extract_keywords_from_input(user_input=user_input)
    print(f"Extracted keywords from input: {keywords}")
    cvs = get_cv_by_keywords(keywords=keywords)
    for cv in cvs:
        print(cv)
"""

url = "http://127.0.0.1:8000"
controller = LocalResumeController(url)
resumes = controller.get_pdfs()
pdf = (resumes[0])