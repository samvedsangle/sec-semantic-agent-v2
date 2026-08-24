import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_classic.chains import RetrievalQA

def run_sec_semantic_agent(query_text: str):
    print("Loading raw SEC documents from disk...")
    loader = DirectoryLoader(
        "./sec-edgar-filings",
        glob="**/*.txt",
        loader_cls=TextLoader,
        show_progress=True
    )
    docs = loader.load()
    print(f"Loaded {len(docs)} document pages/sections.")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    splits = splits[:150]
    print(f"Restricted to {len(splits)} semantic chunks for free-tier processing.")

    print("Embedding chunks locally using SentenceTransformers...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory="./chroma_db_local"
    )
    
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0)

    # Use standard stable RetrievalQA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )

    print(f"\nExecuting query: '{query_text}'\n")
    response = qa_chain.invoke({"query": query_text})
    
    print("--- SEC AGENT AUDIT RESPONSE ---")
    print(response["result"])
    print("--------------------------------")

if __name__ == "__main__":
    sample_query = "What specific supply chain concentration or operational risks were highlighted by the company?"
    run_sec_semantic_agent(sample_query)
