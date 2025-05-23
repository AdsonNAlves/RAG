import os
import glob
import psycopg2
from dotenv import load_dotenv
from langchain.docstore.document import Document
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Milvus
from pymilvus import connections, utility
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain,LLMChain
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate,PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain_community.chat_models import ChatOllama

import gradio as gr

# Carregar variáveis de ambiente do .env
load_dotenv()

POSTGRES_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
    "dbname": os.getenv("POSTGRES_DB", "app_db"),
    "user": os.getenv("POSTGRES_USER", "admin"),
    "password": os.getenv("POSTGRES_PASSWORD", "admin")
}

# Conecta o PostgreSQL e buscar dados de todas as tabelas
def load_postgres_documents():
    conn = psycopg2.connect(**POSTGRES_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
    tables = [row[0] for row in cursor.fetchall()]
    
    documents_pg = []
    for table in tables:
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        colnames = [desc[0] for desc in cursor.description]
        for row in rows:
            content = "\n".join(f"{col}: {val}" for col, val in zip(colnames, row))
            documents_pg.append(Document(page_content=content, metadata={"source": "postgresql", "doc_type": table}))
    
    cursor.close()
    conn.close()
    return documents_pg

# Carregar arquivos .md de cada pasta
def load_markdown_documents():
    folders = glob.glob("knowledge_base/*")
    text_loader_kwargs = {'encoding': 'utf-8'}
    documents = []

    def add_metadata(doc, doc_type):
        doc.metadata["doc_type"] = doc_type
        return doc

    for folder in folders:
        doc_type = os.path.basename(folder)
        loader = DirectoryLoader(folder, glob="**/*.md", loader_cls=TextLoader, loader_kwargs=text_loader_kwargs)
        folder_docs = loader.load()
        documents.extend([add_metadata(doc, doc_type) for doc in folder_docs])
    
    return documents

# Dividir os documentos em chunks
def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, separators=["\n\n","\n","."," ", ""])
    return splitter.split_documents(documents)

milvus_host = os.getenv("MILVUS_HOST", "milvus")
milvus_port = os.getenv("MILVUS_PORT", "19530")

# Conectar ao Milvus
def connect_to_milvus():
    connections.connect(host=milvus_host, port=milvus_port)

# Inserir documentos vetoriais no Milvus
def insert_into_milvus(chunks,collection_name="prediza_chunks", allow_append=False):
    embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
    
    if utility.has_collection(collection_name):
        print(f"[INFO] A coleção '{collection_name}' já existe")
        if allow_append:
            print("[INFO] Inserindo novos documentos na coleção existente...")
            vectorstore = Milvus(
                embedding_function=embeddings,
                collection_name=collection_name,
                connection_args={"host": milvus_host, "port": milvus_port}
            )
            vectorstore.add_documents(chunks)

        else:
            print("[INFO] Recuperando a coleção existente sem modificá-la...")
            vectorstore = Milvus(embedding_function=embeddings, collection_name=collection_name, connection_args={"host": milvus_host, "port": milvus_port})
    else:    
        print(f"[INFO] Criando a coleção '{collection_name}' e inserindo documentos...")
        vectorstore = Milvus.from_documents(chunks, embedding=embeddings, collection_name=collection_name, connection_args={"host": milvus_host, "port": milvus_port})
        print("[INFO] Dados inseridos no Milvus com sucesso.")
    return vectorstore

def chat(question, history):
    print("Pergunta recebida:", question)
    result = conversation_chain.invoke({"question": question})
    return result["answer"]

if __name__ == "__main__":
    print("Iniciando pipeline RAG...")

    postgres_docs = load_postgres_documents()
    md_docs = load_markdown_documents()
    all_docs = postgres_docs + md_docs
    chunks = split_documents(all_docs)

    connect_to_milvus()
    vectorstore= insert_into_milvus(chunks,collection_name="prediza_chunks",allow_append=False) # manter allow_append como False

    print("Configurando modelo e cadeia de conversação...")
    
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")

    # LLM
    llm = ChatOllama(temperature=0.7, model="phi4-mini", base_url=ollama_base_url)

    # Prompt customizado traduzido e adaptado

    system_message = (
    "Use os seguintes trechos de contexto para responder à pergunta do usuário.\n"
    "Se você não souber a resposta, diga: 'Não sei. Isso não consta nos dados da Prediza.'\n"
    "Não responda nada fora do contexto fornecido, **exceto**:\n"
    "- Saudações (ex: olá, bom dia)\n"
    "- Perguntas sobre sua identidade (ex: quem é você?), que podem ser respondidas dizendo que você é um assistente que responde com base nos dados da empresa Prediza."
    )


    # Prompt formatado
    system_msg_prompt = SystemMessagePromptTemplate.from_template(system_message)
    human_msg_prompt = HumanMessagePromptTemplate.from_template("Contexto:\n{context}\n\nPergunta: {question}")
    chat_prompt = ChatPromptTemplate.from_messages([system_msg_prompt, human_msg_prompt])

    # Prompt para geração da próxima pergunta com base no histórico
    condense_prompt = PromptTemplate.from_template("""
    Dada a conversa anterior e a nova pergunta de acompanhamento, reformule a nova pergunta de forma independente.
    Histórico do chat: {chat_history} Pergunta de acompanhamento: {question} Pergunta reformulada: """)

    # Cadeias
    question_generator = LLMChain(llm=llm, prompt=condense_prompt)
    qa_chain = StuffDocumentsChain(llm_chain=LLMChain(llm=llm, prompt=chat_prompt), document_variable_name="context")

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True,output_key="answer")
    retriever = vectorstore.as_retriever()

    # Cadeia final com logs
    conversation_chain = ConversationalRetrievalChain(
        retriever=retriever,
        memory=memory,
        question_generator= question_generator,
        combine_docs_chain=qa_chain,
        return_source_documents=True
    )

    print("Pipeline RAG finalizado. Iniciando Gradio...")

    # Interface Gradio
    view = gr.ChatInterface(
        fn=chat,
        chatbot=gr.Chatbot(height=400, type="messages"),
        title="RAG Assistant - Prediza",
        theme="soft",
        description="Faça perguntas sobre insights e dados Prediza.",
        type="messages",
    )
    view.launch(server_name="0.0.0.0", server_port=7863, inbrowser=False)
