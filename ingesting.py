import os
import streamlit as st
from langchain.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# Set persist directory
persist_directory = 'db'

tre_loader = DirectoryLoader('./docs/tre/', glob="*.pdf", recursive=True)

tre_docs = tre_loader.load()

embeddings = OpenAIEmbeddings()
text_splitter = CharacterTextSplitter(chunk_size=250, chunk_overlap=8)

# Split documents and generate embeddings
tre_docs_split = text_splitter.split_documents(tre_docs)

print(tre_docs_split)

#metadata = []
#for doc in tre_docs_split:
#    metadata.append(doc.metadata['source'])
    

# Create Chroma instances and persist embeddings
treDB = Chroma.from_documents(tre_docs_split, embeddings, persist_directory=os.path.join(persist_directory, 'tre'))
treDB.persist()