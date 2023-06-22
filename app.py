import os
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
import streamlit as st
from utils import ensure_fit_tokens, get_page_contents
from prompts import human_template, system_message
from render import user_msg_container_html_template, bot_msg_container_html_template
import openai

# Set OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config("CHATSGP")

hide_streamlit_style = """
                <style>
                div[data-testid="stToolbar"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                #MainMenu {
                visibility: hidden;
                height: 0%;
                }
                header {
                visibility: hidden;
                height: 0%;
                }
                footer {
                visibility: hidden;
                height: 0%;
                }
                </style>
                """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)


hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)



st.title("CHATSGP")

#st.header("CHATSGP")

st.markdown("""<hr style="height:1px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)

# Initialize embeddings
embeddings = OpenAIEmbeddings()

treDB = Chroma(persist_directory=os.path.join('db', 'tre'), embedding_function=embeddings)
tre_retriever = treDB.as_retriever(search_kwargs={"k": 3})


# Initialize session state for chat history
if "history" not in st.session_state:
    st.session_state.history = []

# Construct messages from chat history
def construct_messages(history):
    messages = [{"role": "system", "content": system_message}]
    
    for entry in history:
        role = "user" if entry["is_user"] else "assistant"
        messages.append({"role": role, "content": entry["message"]})
    
    # Ensure total tokens do not exceed model's limit
    messages = ensure_fit_tokens(messages)
    
    return messages


# Define handler functions for each category
def tre_handler(query):
    print("Using TRE-ES handler...")
    # Get relevant documents from TRE's database
    relevant_docs = tre_retriever.get_relevant_documents(query)

    # Use the provided function to prepare the context
    context = get_page_contents(relevant_docs)

    # Prepare the prompt for GPT-3.5-turbo with the context
    query_with_context = human_template.format(query=query, context=context)

    return {"role": "user", "content": query_with_context}

  

# Function to generate response
def generate_response():
    # Append user's query to history
    st.session_state.history.append({
        "message": st.session_state.prompt,
        "is_user": True
    })
    
  
    # Route the query based on category
    new_message = tre_handler(st.session_state.prompt)

    # Construct messages from chat history
    messages = construct_messages(st.session_state.history)
    
    # Add the new_message to the list of messages before sending it to the API
    messages.append(new_message)
    
    # Ensure total tokens do not exceed model's limit
    messages = ensure_fit_tokens(messages)

   
    # Call the Chat Completions API with the messages
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    # Extract the assistant's message from the response
    assistant_message = response['choices'][0]['message']['content']

   
    # Append assistant's message to history
    st.session_state.history.append({
        "message": assistant_message,
        "is_user": False
    })

    #clean prompt
    st.session_state["prompt"] = ""

# Display chat history
for message in st.session_state.history:
    if message["is_user"]:
            st.write(user_msg_container_html_template.replace("$MSG", message["message"]), unsafe_allow_html=True)
    else:
            st.write(bot_msg_container_html_template.replace("$MSG", message["message"]), unsafe_allow_html=True)


# Take user input
st.text_input("",
              key="prompt",
              placeholder="Faça uma pergunta",
              on_change=generate_response
              )