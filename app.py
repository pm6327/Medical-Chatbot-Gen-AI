from flask import Flask, render_template, jsonify, request
from src.helper import download_hugging_face_embeddings
from langchain_pinecone import PineconeVectorStore
# from langchain_openai import OpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from src.prompt import *
import os


app = Flask(__name__)


import warnings
warnings.simplefilter("ignore", category=FutureWarning)



load_dotenv(dotenv_path="C:/Users/91830/Desktop/Medical-Chatbot-Gen-AI/.env")

PINECONE_API_KEY=os.environ.get('PINECONE_API_KEY')
GEMINI_API_KEY=os.environ.get('GEMINI_API_KEY')

os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
print("GEMINI API Key:", os.getenv("GEMINI_API_KEY"))
os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY


# GEMINI_API_KEY = "AIzaSyAKzQ6qKWFN8lZyLYTTkhZY2m23P1F-aJQ"  # Replace with your API key
# os.environ["GEMINI_API_KEY"] = "AIzaSyAKzQ6qKWFN8lZyLYTTkhZY2m23P1F-aJQ" 


embeddings = download_hugging_face_embeddings()


index_name = "medical-chatbot"

# Embed each chunk and upsert the embeddings into your Pinecone index.
docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings
)

retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k":3})


llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0.4, max_output_tokens=500)
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)


@app.route("/")
def index():
    return render_template('chat.html')


# @app.route("/get", methods=["GET", "POST"])
# def chat():
#     msg = request.form["msg"]
#     input = msg
#     print(input)
#     response = rag_chain.invoke({"input": msg})
#     print("Response : ", response["answer"])
#     return str(response["answer"])

@app.route("/get", methods=["GET", "POST"])
def chat():
    try:
        msg = request.form.get("msg", "")  # Get user input safely
        print("\n[DEBUG] User Input:", msg)

        if not msg:
            return "Error: No input received"

        # Check Pinecone Retrieval
        retrieved_docs = retriever.get_relevant_documents(msg)
        print("\n[DEBUG] Retrieved Documents:", retrieved_docs)

        # Check RAG Processing
        response = rag_chain.invoke({"input": msg})
        print("\n[DEBUG] LLM Response:", response)

        return str(response.get("answer", "No response generated"))
    
    except Exception as e:
        print("\n[ERROR]", str(e))
        return f"Error: {str(e)}"




if __name__ == '__main__':
    app.run(host="0.0.0.0", port= 8080, debug= True)