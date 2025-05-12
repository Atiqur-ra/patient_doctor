from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from langchain.docstore.document import Document
from firebase_admin import firestore
from pinecone import Pinecone
from logger import logging
from exception import CustomException
import sys, os
from dotenv import load_dotenv
load_dotenv()


# for initializing Pinecone
pc = Pinecone(
    api_key=os.environ["PINCONE_API"]
)

def handle_document_query(chat_name, question):
    try:
        # fectching index from firebase
        db = firestore.client()
        index_ref = db.collection("document_indices").document(chat_name).get()

        if not index_ref.exists:
            raise ValueError(f"Document index {chat_name} not found")

        index_name = index_ref.to_dict().get("index_name")
        index = pc.Index(index_name)

        # embeding the questioin into vector
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vector_query = embeddings.embed_query(question)

        # Query Pinecone
        search_result = index.query(
            vector=vector_query, namespace=chat_name,top_k=3, include_values=False, include_metadata=True
        )

        docs = [
            Document(page_content=result['metadata']['text'])
            for result in search_result['matches']
            if 'metadata' in result
        ]

        chain = get_conversational_chain()
        response = chain({"input_documents": docs, "question": question}, return_only_outputs=True)

        return response['output_text']

    except Exception as e:
        logging.error(f"Error during document query: {str(e)}")
        raise CustomException(e, sys)

def get_conversational_chain():
    prompt_template = """
    Answer the question as detailed as possible from the provided context. If the answer is not in the provided context, 
    say 'answer is not available in the context'.\n\n
    Context:\n {context}?\n
    Question: \n{question}\n
    Answer:
    """
    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    return load_qa_chain(model, chain_type="stuff", prompt=prompt)