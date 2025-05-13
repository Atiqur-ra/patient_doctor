
from langchain.docstore.document import Document
from pinecone import Pinecone
from langchain_huggingface import HuggingFaceEmbeddings
from logger import logging
from exception import CustomException
import sys, os
from dotenv import load_dotenv
from transformers import pipeline
load_dotenv()





pc = Pinecone(
    api_key=os.getenv("PINCONE_API")
)

os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("HUGGINGFACEHUB_API_TOKEN")

pipe = pipeline("text2text-generation", model="google/flan-t5-large", device="mps")

def handle_document_query(chat_name: str, question: str):
    try:
        index_name = "langchainvector1"
        namespace = chat_name

        index = pc.Index(index_name)

        # Embed the question
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vector_query = embeddings.embed_query(question)

        # Query Pinecone
        search_result = index.query(
            vector=vector_query,
            namespace=namespace,
            top_k=3,
            include_values=False,
            include_metadata=True
        )

        # Convert results to LangChain Document objects
        docs = [
            Document(page_content=result['metadata']['text'])
            for result in search_result['matches']
            if 'metadata' in result
        ]
        
        
        context = "\n".join([doc.page_content for doc in docs])
        input_text = f"Context: {context} \nQuestion: {question}"

        # Use the Hugging Face pipeline to generate the answer
        response = pipe(input_text)

    
        return response[0]['generated_text']

    except Exception as e:
        logging.error(f"Error during document query: {str(e)}")
        raise CustomException(e, sys)


