# CHATSGP: 

CHATSGP é uma aplicação que utiliza o poder do GPT-TURBO para fornecer respostas para os documentos importantes da SGP do TRE-ES. Ela permite aos usuários fazer perguntas e receber respostas de diferentes bases de conhecimento.

## Funcionalidades

- Interface para interagir com o chatbot.
- Templates HTML para exibição do histórico de chat e mensagens.
- Persistência de embeddings usando Chroma vector db.
- Integração com OpenAI.

## Instalação

1. Clone o repositório:

```
git clone https://github.com/fabianocastiglioni/chatsgp.git
```

2. Instale as dependências requeridas:

```
pip install -r requirements.txt
```

3. Configure suas credenciais:

- Acesse o website OpenAI e obtenha uma chave de API.
- Crie um arquivo chamado "secrets.toml" na pasta .streamlit.
- Informe sua chave API da OpenAI no arquivo secrets.toml ou como variável de ambiente.      
  OPENAI_API_KEY="chave"

4. Execute o script indexing para criar um banco de dados de vetor:

```
python ingesting.py
```

Esse script criará as bases de dados de vetor para os documentos da SGP. 
Os documentos devem estar na pasta ./docs/tre/sgp antes de executar o script.

5. Execute a aplicação:

```
streamlit run app.py
```

## Como utilizar

1. Acesse a aplicação ao navegar para `http://localhost:8501` em seu navegador.

2. Entre com seu prompt (pergunta) no campo de entrada e pressione Enter.

3. O chatbot processará sua pergunta e fornecerá uma resposta baseada nas fontes de dados disponíveis.

4. O histórico do chat será exibido na tela, mostrando as mensagens do usuário e do assistente virtual.

