
from langchain.docstore.document import Document
from pinecone import Pinecone
from exception import CustomException
import sys, os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain


load_dotenv()





pc = Pinecone(
    api_key=os.getenv("PINCONE_API")
)


def handle_document_query(chat_name: str, question: str):
    try:
        index_name = "langchainvector1"
        namespace = chat_name

        index = pc.Index(index_name)


        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vector_query = embeddings.embed_query(question)


        search_result = index.query(
            vector=vector_query,
            namespace=namespace,
            top_k=3,
            include_values=False,
            include_metadata=True
        )

        docs = [
            Document(page_content=result['metadata']['text'])
            for result in search_result['matches']
            if 'metadata' in result
        ]
        chain = get_conversational_chain()
        response = chain.invoke({"input_documents": docs, "question": question}, return_only_outputs=True)

        return response['output_text']
        
        

    except Exception as e:
        raise CustomException(e, sys)


def get_conversational_chain():
    prompt_template = """
    Answer the question as detailed as possible from the provided context. If the answer is not in the provided context, 
    say 'answer is not available in the context'.\n\n
    Context:{context}
    Question: {question}
    Answer:
    """
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    return load_qa_chain(model, chain_type="stuff", prompt=prompt)