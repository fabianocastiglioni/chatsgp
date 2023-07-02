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
    #print("relevant docs:")
    #print(relevant_docs)

    # Busca o contexto dos documentos relevantes
    context = get_page_contents(relevant_docs)

    #print("contexto")
    #print(context)
    '''
    if (len(context)>0):
        query_prompt = human_template_context.format(query=query, context=context)
        

    else:
        query_prompt = human_template.format(query=query, context=context)
    '''

    query_prompt = human_template.format(query=query, context=context)
    
    #print("query_prompt:")
    #print(query_prompt)

    new_message =  {"role": "user", "content": query_prompt}
  

    # Constrói as mensagens considerando todo o histórico da conversa
    messages = construct_messages(history)
    
    # Adiciona a nova mensagem à lista de mensagens
    messages.append(new_message)

    print("\nHistory:\n")
    print(history)

    #print(messages)

    #https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/chatgpt?pivots=programming-language-chat-completions
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=.7
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