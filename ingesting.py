import os
import streamlit as st
from langchain.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import pytesseract
from dotenv import load_dotenv



pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

load_dotenv()

# Set persist directory
persist_directory = 'db'

tre_loader = DirectoryLoader('./docs/tre/', glob="*.pdf", recursive=True)

tre_docs = tre_loader.load()

embeddings = OpenAIEmbeddings()

#https://www.pinecone.io/learn/chunking-strategies
text_splitter = CharacterTextSplitter(chunk_size=512, chunk_overlap=50)

# Split documents and generate embeddings
tre_docs_split = text_splitter.split_documents(tre_docs)

print(tre_docs_split)

#metadata = []
#for doc in tre_docs_split:
#    metadata.append(doc.metadata['source'])
    

# Create Chroma instances and persist embeddings
treDB = Chroma.from_documents(tre_docs_split, embeddings, persist_directory=os.path.join(persist_directory, 'tre'))
treDB.persist()