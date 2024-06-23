from llama_index.core import   (
    VectorStoreIndex,
    StorageContext,
    Settings
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
import os
import torch
from transformers import BitsAndBytesConfig
from llama_index.core.prompts import PromptTemplate
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

hf_token = "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"

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
)

llm = HuggingFaceLLM(
    model_name="meta-llama/Llama-2-7b-chat-hf",
    tokenizer_name="meta-llama/Llama-2-7b-chat-hf",
    query_wrapper_prompt=PromptTemplate("<s> [INST] {query_str} [/INST] "),
    context_window=3900,
    model_kwargs={"token": hf_token, "quantization_config": quantization_config},
    tokenizer_kwargs={"token": hf_token},
    device_map="auto",
)

# documents = SimpleDirectoryReader("data").load_data()


db = chromadb.PersistentClient(path="./chroma_db")

# bge-base embedding model
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")

# ollama
Settings.llm = llm

async def create_vectore_store(sessionId,document):
    chroma_collection = db.get_or_create_collection(sessionId)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex.from_documents(
    document, storage_context=storage_context)
    return index


response = query_engine.query("What did the author do growing up?")
print(response)