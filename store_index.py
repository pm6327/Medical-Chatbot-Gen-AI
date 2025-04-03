from src.helper import load_pdf_file, text_split, download_hugging_face_embeddings
# from pinecone.grpc import PineconeGRPC as Pinecone
import pinecone
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
import os


load_dotenv()

pc = pinecone.Pinecone(
    api_key="pcsk_77QdHv_AnNMw9tgfC4NPpqA7WQ37ArnZy44K5KWLtDH9YDNkRz4jC5aVeQehjVGDYZFFBD",
    environment="us-east-1"  # Change this based on your region
)


PINECONE_API_KEY=os.environ.get('PINECONE_API_KEY')
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY


extracted_data=load_pdf_file(data='Data/')
text_chunks=text_split(extracted_data)
embeddings = download_hugging_face_embeddings()


pc = Pinecone(api_key=PINECONE_API_KEY)

index_name = "medical-chatbot"


pc.create_index(
    name=index_name,
    dimension=384, 
    metric="cosine", 
    spec=ServerlessSpec(
        cloud="aws", 
        region="us-east-1"
    ) 
) 

# Embed each chunk and upsert the embeddings into your Pinecone index.
docsearch = PineconeVectorStore.from_documents(
    documents=text_chunks,
    index_name=index_name,
    embedding=embeddings, 
)