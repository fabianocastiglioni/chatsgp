import streamlit as st
from css import css
from PyPDF2 import PdfReader
import requests
import json

def get_pdf_texts(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def ingest(txt):
    url = "http://localhost:5000/ingest"
 
    headers = {"Content-Type": "application/json; charset=utf-8"}
 
    data = {
        "text": txt
    }
 
    response = requests.post(url, headers=headers, json=data)
    return response

def main():
    """ st.set_page_config(page_title="Gerenciamento de base de conhecimento chatbot",
                       page_icon=":books:") """
    st.write(css, unsafe_allow_html=True)

    st.header("Gerenciamento de base de conhecimento chatbot :books:")
    
    with st.sidebar:
        st.subheader("Seus documentos")
        pdf_docs = st.file_uploader(
            "Upload seus PDFs aqui e clique em 'Treinar'", accept_multiple_files=True)
        if st.button("Treinar"):
            with st.spinner("Processando"):
                # get pdf text
                raw_text = get_pdf_texts(pdf_docs)

                response = ingest(raw_text)
                if(response.status_code == 200):
                    st.write("Treinamento concluído com sucesso")
                    st.write(response.text)



if __name__ == '__main__':
    main()
