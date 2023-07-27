from flask import Flask, render_template,request,jsonify
from flask_cors import CORS
import openai
from utils import ensure_fit_tokens, get_page_contents
import os
from langchain.text_splitter import CharacterTextSplitter,RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
#from prompts import human_template, system_message
from novo_prompt import system_message,human_message
from dotenv import load_dotenv
from langchain.document_loaders import DirectoryLoader
import json
import re 

#from langchain.chains import RetrievalQA
#from langchain.llms import OpenAI

app = Flask(__name__)

CORS(app)

load_dotenv()

_vectorStore = None

history = []

def build_vectorstore():
    print(f'Buscando VectorStore...')
    global _vectorStore
    if(_vectorStore is None):
        embeddings = OpenAIEmbeddings()
        _vectorStore = Chroma(persist_directory=os.path.join('db', 'tre'), embedding_function=embeddings)
        print(f'Sigleton de VectorStore...')
    else:
        print(f'Retornando VectorStore...')
    
    
    return _vectorStore

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

@app.get("/")
def index_get():
    return "api running..."

@app.post("/ingest")
def ingest():
    global _vectorStore
    text = request.get_json(force=True).get("text")
    chunks = get_text_chunks(text)
    _vectorStore.add_texts(chunks)
    _vectorStore.persist()
    print(text)
    print()
    print('Ingestão completa')

@app.post("/chat")
def getChatResponse():
    message = request.get_json(force=True).get("message")
    history = request.get_json(force=True).get("messages")
    response = get_response(message,history)

    """ print(f'message:\n {message}')
    print(f'history:\n {history}')
    print(f'response:\n {response}') """


    message = {"answer": response}
    return jsonify(message)


def pesquisaLocalVotacao(nome,nome_mae,data_nascimento):
    print('Pesquisando local de votação...')
    print(nome)
    print(nome_mae)
    print(data_nascimento)
    return "Local 1010- Fernando Duarte Rabelo"

def get_response(query,history):
    global _vectorStore
    # Busca os documentos relevantes(mais similares) à pergunta
    retr = _vectorStore.as_retriever(search_kwargs={"k": 3})
    relevant_docs = retr.get_relevant_documents(query)
    context = get_page_contents(relevant_docs)

    print(f'query:\n {query}')
    print(f'history:\n {history}')
    print(f'context:\n {context}')

    messages = [{"role": "system", "content": system_message.format(context=context)}]
     
    for entry in history:
        role = "user" if entry["name"]=="User" else "assistant"
        messages.append({"role": role, "content": human_message.format(query=entry["message"]) if role == "user" else entry["message"]})

    
    """
        prompt = human_message.format(query=query)
        new_message =  {"role": "user", "content": prompt}
        messages.append(new_message) 
    """


    # Constrói as mensagens considerando todo o histórico da conversa
    #messages = construct_messages(history)
    
    print(f'\nMensagens enviadas para a OpenAI:\n {messages}')

    #https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/chatgpt?pivots=programming-language-chat-completions
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.3
    )

    assistant_message = response['choices'][0]['message']['content']

    print(f'\nResposta Original do assistente:\n {assistant_message}')

    if("pesquisa_local_votacao" in assistant_message):

        print('intenção do usuário foi pesquisar local de votação')
        
        regex = r"\#(.*?)\#"
        matches = re.finditer(regex, assistant_message, re.MULTILINE | re.DOTALL)

        data = None

        for matchNum, match in enumerate(matches):
            for groupNum in range(0, len(match.groups())):
                print (match.group(1))
                data = match.group(1)
                break
        
        if(data):
            split_data = data.split(',')
            nome_completo = split_data[1].split(':')[1]
            
            split_nome_completo = nome_completo.split(' ')
            if (len(split_nome_completo)>1):
                primeiro_nome = split_nome_completo[0]
            else:
                primeiro_nome = nome_completo
                

            nome_mae = split_data[2].split(':')[1]
            data_nascimento = split_data[3].split(':')[1]
            local_votacao = pesquisaLocalVotacao(nome_completo,nome_mae,data_nascimento)
            assistant_message = "Obrigada por confirmar,{primeiro_nome}}.\n Com base nas informações fornecidas, irei realizar uma pesquisa para encontrar o seu local de votação. \nPor favor, aguarde um momento. [Realizando a pesquisa...] \nEncontrei o seu local de votação:\n {local_votacao}".format(primeiro_nome=primeiro_nome,local_votacao=local_votacao)
            #assistant_message = "Seu local de votação é:\n {local_votacao}".format(local_votacao = local_votacao)
        else:
            assistant_message = "Não foi possível localizar o seu local de votação"

        
        print(f'\nResposta da pesquisa de local de votação:\n {assistant_message}')
        

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
        #contents += f"Document {doc.metadata['source']}:\n{doc.page_content}\n\n"
        contents += f"Document:\n{doc.page_content}\n\n"
    return contents   

build_vectorstore()

if __name__ == "__main__":
    app.run(debug=True)