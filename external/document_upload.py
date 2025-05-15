# from PyPDF2 import PdfReader
from pypdf import PdfReader
from logger import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec
from exception import CustomException
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from database import get_db
from models.document_index_model import DocumentIndex
from langchain_community.embeddings import HuggingFaceEmbeddings
from fastapi import Depends
import sys
import os


load_dotenv()

pc = Pinecone(
    api_key=os.getenv("PINCONE_API"),
)

index_name = 'langchainvector1'


if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,
        metric='cosine',
        spec=ServerlessSpec(cloud='aws', region='us-east-1')
    )

def handle_document_upload(uploaded_file, chat_name: str, patient_id: int, db: Session=Depends(get_db)):
    try:
        if uploaded_file.name.endswith('.pdf'):
            text = extract_pdf_text(uploaded_file)
            text_chunks = split_text_into_chunks(text)

            index = pc.Index(index_name)
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            vectors = embeddings.embed_documents(text_chunks)

            upsert_data = [
                {"id": f"{chat_name}_{i}", "values": vector, "metadata": {"text": text_chunks[i]}}
                for i, vector in enumerate(vectors)
            ]
            index.upsert(vectors=upsert_data, namespace=chat_name)

            db_index = DocumentIndex(patient_id=patient_id, chat_name=chat_name, index_name=index_name)
            db.add(db_index)
            db.commit()
    except Exception as e:
        raise CustomException(e, sys)

def extract_pdf_text(pdf_file):
    text = ""
    pdf_reader = PdfReader(pdf_file)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def split_text_into_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    return text_splitter.split_text(text)