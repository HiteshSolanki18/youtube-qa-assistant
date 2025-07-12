from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
import os
from dotenv import load_dotenv

load_dotenv()

def split_text(text: str, chunk_size=500, chunk_overlap=100):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.create_documents([text])

def setup_vector_store(video_id: str, texts):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    collection_name = f"video_{video_id}"
    persist_dir = "./chroma_langchain_db"

    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=persist_dir,
    )

    # Avoid duplicate insert
    if len(vector_store.get()["ids"]) == 0:
        vector_store.add_documents(texts)

    return vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 5})