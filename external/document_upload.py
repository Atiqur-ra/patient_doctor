from PyPDF2 import PdfReader
from logger import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pinecone import Pinecone, ServerlessSpec
from exception import CustomException
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from database import get_db
from models.document_index_model import DocumentIndex
from langchain_community.embeddings import HuggingFaceEmbeddings

import sys
import os


load_dotenv()

# for initializing Pinecone
pc = Pinecone(
    api_key="pcsk_3um4hy_NirYyZX1yqKQ5mfLse4t5icdao8xNLPCSNPaZ2wZSY9cfYmVZrTm8Yn5zhqbKEv"
)

index_name = 'langchainvector1'

# for checking the index exits or not
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,
        metric='cosine',
        spec=ServerlessSpec(cloud='aws', region='us-east-1')
    )

def handle_document_upload(uploaded_file, chat_name: str, patient_id: int, db: Session):
    try:
        text = extract_pdf_text(uploaded_file)
        text_chunks = split_text_into_chunks(text)

        index = pc.Index(index_name)
        # embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectors = embeddings.embed_documents(text_chunks)

        upsert_data = [
            {"id": f"{chat_name}_{i}", "values": vector, "metadata": {"text": text_chunks[i]}}
            for i, vector in enumerate(vectors)
        ]
        index.upsert(vectors=upsert_data, namespace=chat_name)

        # Store metadata in PostgreSQL
        db_index = DocumentIndex(patient_id=patient_id, chat_name=chat_name, index_name=index_name)
        db.add(db_index)
        db.commit()

        logging.info(f"Document {chat_name} indexed successfully")
    except Exception as e:
        logging.error(f"Error during document upload: {str(e)}")
        raise CustomException(e, sys)

#  to extract text from PDF
def extract_pdf_text(pdf_file):
    text = ""
    pdf_reader = PdfReader(pdf_file)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# to split text into chunks
def split_text_into_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    return text_splitter.split_text(text)