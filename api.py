from flask import Flask, render_template,request,jsonify
from flask_cors import CORS
import openai
from utils import ensure_fit_tokens, get_page_contents
import os
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from prompts import human_template, system_message
from dotenv import load_dotenv

#from langchain.chains import RetrievalQA
#from langchain.llms import OpenAI

app = Flask(__name__)

CORS(app)

load_dotenv()

# Define the folder for storing database
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY
embeddings = OpenAIEmbeddings()
db = Chroma(persist_directory=os.path.join('db', 'tre'), embedding_function=embeddings)
retriever = db.as_retriever(search_kwargs={"k": 3})

history = []

@app.get("/")
def index_get():
    return "api running..."

@app.post("/chat")
def getChatResponse():
    message = request.get_json(force=True).get("message")
    history = request.get_json(force=True).get("messages")
    response = get_response(message,history)
    message = {"answer": response}
    return jsonify(message)

def get_response(query,history):


    # Busca os documentos relevantes(mais similares) à pergunta
    relevant_docs = retriever.get_relevant_documents(query)

    '''
    qa = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type="stuff", retriever=retriever)
    query = "Qual o prazo para tomar posse?"
    print(qa.run(query))

    '''
    print("relevant docs:")
    print(relevant_docs)

    # Busca o contexto dos documentos relevantes
    context = get_page_contents(relevant_docs)

    # Prepara o prompt com o contexto
    query_with_context = human_template.format(query=query, context=context)

    # Monta mensagem com contexto
    new_message =  {"role": "user", "content": query_with_context}

    # Constrói as mensagens considerando todo o histórico da conversa
    messages = construct_messages(history)
    
    # Adiciona a nova mensagem à lista de mensagens
    messages.append(new_message)

    print(messages)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    assistant_message = response['choices'][0]['message']['content']

    return assistant_message

# Construct messages from chat history
def construct_messages(history):
    
    #caso exista apenas a primeira mensagem do usuário do history, podemos remover, pois ela será adicionada depois.
    if( len(history) == 1 ):
        history.pop()
    
    messages = [{"role": "system", "content": system_message}]
    
    for entry in history:
        role = "user" if entry["name"]=="User" else "assistant"
        messages.append({"role": role, "content": entry["message"]})
    
    # Ensure total tokens do not exceed model's limit
    #messages = ensure_fit_tokens(messages)
    
    return messages

def get_page_contents(docs):
    contents = ""
    for i, doc in enumerate(docs, 1):
        contents += f"Document {doc.metadata['source']}:\n{doc.page_content}\n\n"
    return contents

if __name__ == "__main__":
    app.run(debug=True)